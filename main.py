"""
main.py
Orchestrates the full KYC Risk Scoring Engine pipeline.

Run with:  python main.py

Steps:
  1. Load and preprocess the dataset
  2. Engineer 8 composite features
  3. Compute weighted risk scores (0-100)
  4. Train & compare 3 ML classifiers, select champion
  5. Generate SHAP explainability
  6. Write kyc_output.csv

BNY Hackathon 2026 · Antigravity Team
"""

import pandas as pd
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.preprocessor     import preprocess
from src.feature_engineer import engineer_features
from src.scorer           import score_customers
from src.model            import run_model_pipeline
from src.explainer        import run_explainer_pipeline

# ── Configuration ──────────────────────────────────────────────────────────────
INPUT_CSV  = 'data/kyc_industry_dataset.csv'
OUTPUT_CSV = 'output/kyc_output.csv'
OUTPUT_DIR = 'output/'

os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    start_time = time.time()
    
    print("=" * 65)
    print("  🏦 Smart KYC Risk Scoring Engine — BNY Hackathon 2026")
    print("  Antigravity Team · AI-powered AML Customer Onboarding")
    print("=" * 65)

    # ── Step 1: Preprocessing ─────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Step 1/5] Preprocessing data...")
    print("─" * 65)
    df = preprocess(INPUT_CSV)

    # ── Step 2: Feature engineering ───────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Step 2/5] Engineering 8 composite features...")
    print("─" * 65)
    df = engineer_features(df)

    # ── Step 3: Risk scoring ──────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Step 3/5] Computing weighted risk scores (0-100)...")
    print("─" * 65)
    df = score_customers(df)

    # ── Step 4: ML model ──────────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Step 4/5] Training & comparing 3 ML classifiers...")
    print("─" * 65)
    df, model, X, features = run_model_pipeline(df)

    # ── Step 5: Explainability ────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Step 5/5] Generating SHAP explanations...")
    print("─" * 65)
    explanations = run_explainer_pipeline(df, model, X, features, OUTPUT_DIR)
    df['top_risk_factors'] = explanations

    # ── Write output CSV ──────────────────────────────────────────────────────
    output_cols = [
        'customer_id',
        'risk_score',
        'final_risk_tier',   # ML + rule-based combined
        'decision',
        'top_risk_factors',
        # Extra columns for dashboard (bonus analytics)
        'age', 'country_risk', 'occupation', 'annual_income',
        'account_type', 'document_status', 'address_verified',
        'pep_flag', 'sanctions_flag', 'adverse_media_flag',
        'customer_tenure_years', 'digital_risk_score',
        'fraud_history_flag', 'monthly_txn_count',
    ]
    # Only keep columns that exist
    output_cols = [c for c in output_cols if c in df.columns]
    df_out = df[output_cols].rename(columns={'final_risk_tier': 'risk_tier'})

    df_out.to_csv(OUTPUT_CSV, index=False)
    
    elapsed = time.time() - start_time

    # ── Print final summary ───────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  ✅ PIPELINE COMPLETE — SUMMARY")
    print("=" * 65)
    print(f"\n  Output: {OUTPUT_CSV}")
    print(f"  Total customers processed: {len(df_out)}")
    print(f"  Columns: {len(df_out.columns)}")
    print(f"  Pipeline runtime: {elapsed:.1f}s")
    print()
    print("  Risk Tier Distribution:")
    for tier, count in df_out['risk_tier'].value_counts().items():
        pct = count / len(df_out) * 100
        print(f"    {tier:8s}  {count:4d}  ({pct:.1f}%)")
    print()
    print("  Decision Distribution:")
    for dec, count in df_out['decision'].value_counts().items():
        pct = count / len(df_out) * 100
        print(f"    {dec:15s}  {count:4d}  ({pct:.1f}%)")
    print()
    print("  SHAP plots saved to output/")
    print("  Run dashboard with:  streamlit run dashboard.py")
    print("=" * 65)


if __name__ == '__main__':
    main()
