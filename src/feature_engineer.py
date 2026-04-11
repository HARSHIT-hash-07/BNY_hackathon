"""
feature_engineer.py
Creates 8 composite features that capture real-world AML patterns.
These engineered features are what elevate the model accuracy and
give us meaningful explainability for judges.

Input:  preprocessed DataFrame (output of preprocessor.py)
Output: DataFrame with 8 new feature columns added
"""

import pandas as pd
import numpy as np


def add_compliance_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Composite of the 3 most critical AML flags.
    Range: 0 (clean) to 3 (all three flags raised).
    A score of 3 almost certainly means HIGH tier.
    """
    df = df.copy()
    df['compliance_risk_score'] = (
        df['pep_flag'] +
        df['sanctions_flag'] +
        df['adverse_media_flag']
    )
    return df


def add_document_completeness_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combines document status + address verification.
    Higher = worse (more incomplete identity verification).
    Missing docs AND unverified address = maximum flag.
    """
    df = df.copy()
    # document_status_encoded: 0=Complete, 1=Partial, 2=Missing
    # address_verified: 1=verified (good), 0=unverified (bad)
    # We invert address_verified so that higher = riskier
    df['doc_completeness_score'] = (
        df['document_status_encoded'] +
        (1 - df['address_verified'])
    )
    return df


def add_txn_income_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Behavioural signal: monthly transactions vs declared monthly income.
    A customer with low income making hundreds of transactions per month
    is a classic money laundering pattern (structuring).
    Higher ratio = more suspicious.
    """
    df = df.copy()
    monthly_income = df['annual_income'] / 12
    # Avoid division by zero
    monthly_income = monthly_income.replace(0, 1)
    df['txn_income_ratio'] = df['monthly_txn_count'] / monthly_income
    # Cap at 99th percentile to handle extreme outliers
    cap = df['txn_income_ratio'].quantile(0.99)
    df['txn_income_ratio'] = df['txn_income_ratio'].clip(upper=cap)
    return df


def add_new_customer_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    New customers (tenure = 0) are statistically higher risk.
    No relationship history = no behavioural baseline to compare against.
    """
    df = df.copy()
    df['is_new_customer'] = (df['customer_tenure_years'] == 0).astype(int)
    return df


def add_age_risk_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bin age into 3 risk groups.
    Very young (<20): limited financial history, susceptible to exploitation.
    Normal (20-60): standard risk.
    Senior (>60): potentially targeted for elder fraud.
    """
    df = df.copy()
    conditions = [
        df['age'] <= 20,          # Very young — elevated risk
        df['age'] <= 60,          # Normal age range
        df['age'] > 60            # Senior — elevated risk
    ]
    choices = [1, 0, 1]
    df['age_risk_group'] = np.select(conditions, choices, default=0)
    return df


def add_high_risk_occupation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cash Business = highest AML risk occupation.
    Cash-intensive businesses are classic money laundering vehicles.
    133 customers in the dataset fall into this category.
    """
    df = df.copy()
    df['high_risk_occupation'] = (df['occupation'] == 'Cash Business').astype(int)
    return df


def add_complex_account_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corporate and NRI accounts have higher compliance requirements
    due to cross-border transaction patterns and complex ownership structures.
    261 accounts fall in this category.
    """
    df = df.copy()
    df['complex_account'] = df['account_type'].isin(['Corporate', 'NRI']).astype(int)
    return df


def add_income_occupation_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    """
    🆕 INNOVATION: Detects income-occupation mismatches.
    A student declaring ₹40L annual income is suspicious.
    A salaried employee with extremely low income in a corporate account
    is also a red flag.
    
    Method: Flag anyone whose income is > 2× the median for their
    occupation group (suspiciously high) or < 0.25× median (suspiciously low).
    """
    df = df.copy()
    # Compute median income per occupation
    occupation_medians = df.groupby('occupation')['annual_income'].transform('median')
    
    # Flag anomalies: income > 2x median OR income < 0.25x median
    df['income_occupation_anomaly'] = (
        (df['annual_income'] > 2 * occupation_medians) |
        (df['annual_income'] < 0.25 * occupation_medians)
    ).astype(int)
    
    anomaly_count = df['income_occupation_anomaly'].sum()
    print(f"[FeatureEngineer] Income-occupation anomalies detected: {anomaly_count}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master function — runs all 8 feature engineering steps.
    Call this from main.py after preprocessing.
    """
    df = add_compliance_risk_score(df)
    df = add_document_completeness_score(df)
    df = add_txn_income_ratio(df)
    df = add_new_customer_flag(df)
    df = add_age_risk_group(df)
    df = add_high_risk_occupation(df)
    df = add_complex_account_flag(df)
    df = add_income_occupation_anomaly(df)
    print(f"[FeatureEngineer] 8 composite features added. Shape: {df.shape}")
    return df
