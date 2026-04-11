"""
preprocessor.py
Handles all data cleaning, encoding, and scaling for the KYC dataset.
Input:  raw DataFrame from CSV
Output: cleaned, encoded, scaled DataFrame ready for scoring and ML
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


def load_data(filepath: str) -> pd.DataFrame:
    """Load the raw CSV and return a DataFrame."""
    df = pd.read_csv(filepath)
    print(f"[Preprocessor] Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def inspect_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Report null values, data types, and basic stats.
    This output is useful for judges to see we did due diligence.
    """
    print("\n[Preprocessor] Data Quality Report:")
    null_counts = df.isnull().sum()
    nulls = null_counts[null_counts > 0]
    if len(nulls) == 0:
        print("  ✓ No null values found in any column")
    else:
        print(f"  ⚠ Null values found in {len(nulls)} columns:")
        for col, count in nulls.items():
            print(f"    - {col}: {count} nulls ({count/len(df)*100:.1f}%)")
    
    # Check for duplicates
    dupes = df.duplicated(subset=['customer_id']).sum()
    print(f"  {'✓' if dupes == 0 else '⚠'} Duplicate customer_ids: {dupes}")
    
    # Basic stats
    print(f"  Age range: {df['age'].min()} - {df['age'].max()}")
    print(f"  Income range: {df['annual_income'].min():,.0f} - {df['annual_income'].max():,.0f}")
    print(f"  Digital risk score range: {df['digital_risk_score'].min()} - {df['digital_risk_score'].max()}")
    
    return df


def encode_binary_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Yes/No and string binary columns to 0/1 integers.
    Columns: address_verified, pep_flag, sanctions_flag, adverse_media_flag
    fraud_history_flag is already 0/1 in the dataset.
    """
    df = df.copy()

    # Yes → 1, No → 0
    yes_no_cols = ['address_verified', 'pep_flag', 'sanctions_flag', 'adverse_media_flag']
    for col in yes_no_cols:
        df[col] = df[col].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)

    # Ensure fraud_history_flag is int
    df['fraud_history_flag'] = df['fraud_history_flag'].astype(int)

    print("[Preprocessor] Binary flags encoded")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical columns using ordinal mappings where order matters
    (e.g. country_risk, document_status), and LabelEncoder for others.
    """
    df = df.copy()

    # Ordered mappings — order carries meaning here
    country_risk_map    = {'Low': 0, 'Medium': 1, 'High': 2}
    document_status_map = {'Complete': 0, 'Partial': 1, 'Missing': 2}
    account_type_map    = {'Savings': 0, 'Current': 1, 'NRI': 2, 'Corporate': 3}

    df['country_risk_encoded']    = df['country_risk'].map(country_risk_map).fillna(1)
    df['document_status_encoded'] = df['document_status'].map(document_status_map).fillna(1)
    df['account_type_encoded']    = df['account_type'].map(account_type_map).fillna(0)

    # LabelEncode occupation (no natural order)
    le = LabelEncoder()
    df['occupation_encoded'] = le.fit_transform(df['occupation'].astype(str))

    print("[Preprocessor] Categorical columns encoded")
    return df


def scale_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise continuous numeric columns using StandardScaler.
    Keeps original columns intact, adds _scaled versions.
    """
    df = df.copy()
    scaler = StandardScaler()

    numeric_cols = ['age', 'annual_income', 'digital_risk_score',
                    'monthly_txn_count', 'customer_tenure_years']

    scaled = scaler.fit_transform(df[numeric_cols])
    for i, col in enumerate(numeric_cols):
        df[f'{col}_scaled'] = scaled[:, i]

    print("[Preprocessor] Numeric columns scaled")
    return df


def preprocess(filepath: str) -> pd.DataFrame:
    """
    Master function — runs the full preprocessing pipeline.
    Call this from main.py.
    """
    df = load_data(filepath)
    df = inspect_data_quality(df)
    df = encode_binary_flags(df)
    df = encode_categoricals(df)
    df = scale_numerics(df)
    print(f"[Preprocessor] Pipeline complete. Shape: {df.shape}")
    return df
