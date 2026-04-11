"""
scorer.py
Computes a weighted risk score (0-100) for each customer.
Also assigns the risk tier (LOW / MEDIUM / HIGH) and
the onboarding decision (APPROVE / MANUAL_REVIEW / REJECT / EDD).

IMPORTANT RULE: if sanctions_flag == 1, force score >= 85.
This is a regulatory hard rule — no sanctioned customer can ever
slip below HIGH tier regardless of other signals.

Weight Justification:
─────────────────────
| Feature                   | Weight | Tier     | Why                                                    |
|---------------------------|--------|----------|--------------------------------------------------------|
| sanctions_flag            | 25     | CRITICAL | Regulatory mandate — missing one = massive fine        |
| fraud_history_flag        | 20     | CRITICAL | 52% prevalence — strongest predictor in data           |
| pep_flag                  | 12     | HIGH     | Politically exposed persons always need elevated review |
| adverse_media_flag        | 8      | HIGH     | Negative press = reputational + fraud risk             |
| document_status           | 8      | HIGH     | Missing/partial docs = identity verification failure   |
| country_risk              | 7      | MEDIUM   | Geography is a standard AML signal                     |
| digital_risk_score        | 6      | MEDIUM   | Device/network fraud — rising in digital banking       |
| address_verified          | 5      | MEDIUM   | Unverified address = fraud indicator                   |
| txn_income_ratio          | 3      | LOW      | Behavioural mismatch                                   |
| age_risk_group            | 2      | LOW      | Minor uplift for edge groups                           |
| high_risk_occupation      | 2      | LOW      | Cash business uplift                                   |
| complex_account           | 1      | LOW      | Corporate/NRI slight uplift                            |
| is_new_customer           | 1      | LOW      | New = no baseline                                      |
| TOTAL                     | 100    |          |                                                        |
"""

import pandas as pd
import numpy as np


# ── Weight configuration ───────────────────────────────────────────────────────
# Weights sum to 100. Each weight represents the maximum contribution
# of that feature when it is at its highest risk value.
FEATURE_WEIGHTS = {
    'sanctions_flag':          25,   # CRITICAL
    'fraud_history_flag':      20,   # CRITICAL
    'pep_flag':                12,   # HIGH
    'adverse_media_flag':       8,   # HIGH
    'document_status_encoded':  8,   # HIGH  (0=good, 2=worst)
    'country_risk_encoded':     7,   # MEDIUM (0=good, 2=worst)
    'digital_risk_score':       6,   # MEDIUM (0-100 raw)
    'address_verified':         5,   # MEDIUM (inverted: 0=unverified=bad)
    'txn_income_ratio':         3,   # LOW
    'age_risk_group':           2,   # LOW
    'high_risk_occupation':     2,   # LOW
    'complex_account':          1,   # LOW
    'is_new_customer':          1,   # LOW
}

# ── Tier thresholds ───────────────────────────────────────────────────────────
# Data-adaptive thresholds based on score distribution analysis:
# P60 of scores ≈ 28 (divide LOW from MEDIUM)
# P85 of scores ≈ 38 (divide MEDIUM from HIGH)
# This creates a realistic distribution where ~60% auto-approve, ~25% need review,
# and ~15% get flagged — consistent with real-world banking onboarding rates.
TIER_THRESHOLDS = {
    'LOW':    (0,  24.99),   # → APPROVE
    'MEDIUM': (25, 39.99),   # → MANUAL_REVIEW
    'HIGH':   (40, 100),     # → REJECT or EDD
}

SANCTIONS_FLOOR = 85  # Hard rule: sanctioned customers always score >= 85


def normalise_feature(series: pd.Series, max_val: float) -> pd.Series:
    """Normalise a feature to 0-1 range given its known maximum value."""
    return (series / max_val).clip(0, 1)


def compute_risk_scores(df: pd.DataFrame) -> pd.Series:
    """
    Compute weighted risk score for every customer.
    Returns a Series of scores between 0 and 100.

    Formula:
        score = Σ (normalised_feature_value × weight)
    Each normalised feature contributes up to its weight in points.
    """
    df = df.copy()
    score = pd.Series(0.0, index=df.index)

    # Binary flags (already 0/1) — contribute full weight when flagged
    binary_features = [
        'sanctions_flag', 'fraud_history_flag', 'pep_flag',
        'adverse_media_flag', 'age_risk_group', 'high_risk_occupation',
        'complex_account', 'is_new_customer'
    ]
    for feat in binary_features:
        if feat in FEATURE_WEIGHTS and feat in df.columns:
            score += df[feat] * FEATURE_WEIGHTS[feat]

    # address_verified is inverted — unverified (0) = risk
    if 'address_verified' in df.columns:
        score += (1 - df['address_verified']) * FEATURE_WEIGHTS['address_verified']

    # Ordinal encoded features — normalise by their max value
    if 'document_status_encoded' in df.columns:
        score += normalise_feature(df['document_status_encoded'], 2) * \
                 FEATURE_WEIGHTS['document_status_encoded']

    if 'country_risk_encoded' in df.columns:
        score += normalise_feature(df['country_risk_encoded'], 2) * \
                 FEATURE_WEIGHTS['country_risk_encoded']

    # digital_risk_score is already 0-100
    if 'digital_risk_score' in df.columns:
        score += normalise_feature(df['digital_risk_score'], 100) * \
                 FEATURE_WEIGHTS['digital_risk_score']

    # txn_income_ratio — normalise by 99th percentile cap
    if 'txn_income_ratio' in df.columns:
        cap = df['txn_income_ratio'].quantile(0.99)
        if cap > 0:
            score += normalise_feature(df['txn_income_ratio'], cap) * \
                     FEATURE_WEIGHTS['txn_income_ratio']

    # Apply sanctions hard floor — regulatory requirement
    score = score.where(df['sanctions_flag'] == 0,
                        other=score.clip(lower=SANCTIONS_FLOOR))

    # Final clip to 0-100 range
    return score.clip(0, 100).round(2)


def assign_risk_tier(score: pd.Series) -> pd.Series:
    """Map each score to LOW / MEDIUM / HIGH tier."""
    def tier(s):
        if s < 25:
            return 'LOW'
        elif s < 40:
            return 'MEDIUM'
        else:
            return 'HIGH'
    return score.apply(tier)



def assign_decision(tier: pd.Series, df: pd.DataFrame) -> pd.Series:
    """
    Map each tier to an onboarding decision.
    - Sanctions flag == 1 results in immediate REJECT.
    - Other HIGH risk factors (without active sanctions) go to EDD (Enhanced Due Diligence).
    - MEDIUM risk factors go to MANUAL_REVIEW.
    - LOW risk factors go to APPROVE.
    """
    def decision(row):
        # Regulatory priority: Sanctions are a hard stop.
        if row['sanctions_flag'] == 1:
            return 'REJECT'
            
        if row['risk_tier'] == 'LOW':
            return 'APPROVE'
        elif row['risk_tier'] == 'MEDIUM':
            return 'MANUAL_REVIEW'
        elif row['risk_tier'] == 'HIGH':
            return 'EDD'
        else:
            return 'REJECT'

    combined = pd.DataFrame({'risk_tier': tier, 'sanctions_flag': df['sanctions_flag']})
    return combined.apply(decision, axis=1)



def score_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master function — computes score, tier, and decision for all customers.
    Returns DataFrame with three new columns added.
    """
    df = df.copy()
    df['risk_score'] = compute_risk_scores(df)
    df['risk_tier']  = assign_risk_tier(df['risk_score'])
    df['decision']   = assign_decision(df['risk_tier'], df)

    # Print distribution for quick sanity check
    print("\n[Scorer] Risk Tier Distribution:")
    print(df['risk_tier'].value_counts().to_string())
    print(f"\n[Scorer] Decision Distribution:")
    print(df['decision'].value_counts().to_string())
    
    # Sanity check: all sanctioned customers should be HIGH + EDD
    sanctioned = df[df['sanctions_flag'] == 1]
    if len(sanctioned) > 0:
        all_high = (sanctioned['risk_tier'] == 'HIGH').all()

        all_reject = (sanctioned['decision'] == 'REJECT').all()
        print(f"\n[Scorer] Sanctions check: {len(sanctioned)} sanctioned customers")
        print(f"  All HIGH tier: {'✓' if all_high else '✗ FAIL'}")
        print(f"  All REJECT decision: {'✓' if all_reject else '✗ FAIL'}")

    
    return df
