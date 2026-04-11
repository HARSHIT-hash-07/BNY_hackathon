"""
explainer.py
Generates explainability output for every MEDIUM and HIGH risk customer.

Two outputs:
1. top_risk_factors column — plain-English reasons for the output CSV
2. SHAP plots — saved as PNG files for the dashboard to display

Uses SHAP (SHapley Additive exPlanations) — the industry standard
for explaining tree-based ML models.
"""

import pandas as pd
import numpy as np
import shap
import matplotlib
matplotlib.use('Agg')   # Non-interactive backend for saving files
import matplotlib.pyplot as plt
import os


# Human-readable labels for each feature
# These appear in the plain-English explanation column
FEATURE_LABELS = {
    'sanctions_flag':            'Sanctions flag detected',
    'fraud_history_flag':        'Fraud history present',
    'pep_flag':                  'Politically Exposed Person (PEP)',
    'adverse_media_flag':        'Adverse media / negative news',
    'document_status_encoded':   'Incomplete or missing documents',
    'country_risk_encoded':      'High-risk country of origin',
    'digital_risk_score':        'Elevated digital/network risk score',
    'address_verified':          'Address not verified',
    'txn_income_ratio':          'Transactions disproportionate to income',
    'compliance_risk_score':     'Multiple compliance flags triggered',
    'doc_completeness_score':    'Document completeness issues',
    'age_risk_group':            'Age group elevated risk',
    'high_risk_occupation':      'Cash-intensive occupation',
    'complex_account':           'Complex account type (NRI/Corporate)',
    'is_new_customer':           'New customer — no relationship history',
    'risk_score':                'Overall weighted risk score elevated',
    'income_occupation_anomaly': 'Income-occupation mismatch detected',
    'age':                       'Age-related risk factor',
    'annual_income':             'Unusual income level',
    'monthly_txn_count':         'High transaction volume',
    'customer_tenure_years':     'Short customer tenure',
    'occupation_encoded':        'Occupation risk factor',
    'account_type_encoded':      'Account type risk factor',
}


def compute_shap_values(model, X: pd.DataFrame):
    """
    Compute SHAP values for all customers using TreeExplainer.
    TreeExplainer is optimised for XGBoost — fast and accurate.
    Returns shap_values array of shape (n_customers, n_features, n_classes).
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    print(f"[Explainer] SHAP values computed for {len(X)} customers")
    return explainer, shap_values


def get_top_risk_factors(shap_row: np.ndarray, feature_names: list,
                          n_factors: int = 3) -> str:
    """
    For a single customer (one row of SHAP values), return the
    top N contributing features as a plain-English comma-separated string.

    Only returns factors that pushed the risk UP (positive SHAP = more risky).
    """
    # Pair feature names with their SHAP values
    pairs = list(zip(feature_names, shap_row))
    # Sort by SHAP value descending — highest positive contribution first
    pairs.sort(key=lambda x: x[1], reverse=True)
    # Take top N with positive contributions
    top = [(feat, val) for feat, val in pairs[:n_factors] if val > 0]

    if not top:
        return "No significant risk flags identified"

    reasons = []
    for feat, val in top:
        label = FEATURE_LABELS.get(feat, feat.replace('_', ' ').title())
        reasons.append(label)

    return ", ".join(reasons)


def generate_explanations(df: pd.DataFrame, shap_values, X: pd.DataFrame,
                           features: list) -> pd.Series:
    """
    Generate plain-English top_risk_factors for every customer.
    MEDIUM and HIGH customers get detailed SHAP-derived reasons.
    LOW customers get a standard 'no flags' message.
    """
    explanations = []

    # For multi-class SHAP, use the class with highest predicted risk
    # shap_values shape: [n_classes][n_samples, n_features] for XGBoost
    if isinstance(shap_values, list):
        # Sum absolute values across classes for overall importance
        abs_shap = np.zeros_like(shap_values[0])
        for sv in shap_values:
            abs_shap += np.abs(sv)
    elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        abs_shap = np.abs(shap_values).sum(axis=2)
    else:
        abs_shap = np.abs(shap_values)

    for i, row in df.iterrows():
        tier = row.get('final_risk_tier', row.get('risk_tier', 'LOW'))

        if tier == 'LOW':
            explanations.append("No significant risk flags identified")
        else:
            idx = X.index.get_loc(i)
            shap_row = abs_shap[idx]
            factors = get_top_risk_factors(shap_row, features, n_factors=3)
            explanations.append(factors)

    return pd.Series(explanations, index=df.index, name='top_risk_factors')


def save_shap_summary_plot(shap_values, X: pd.DataFrame,
                            features: list, output_dir: str = 'output/'):
    """
    Save the SHAP summary beeswarm plot as a PNG.
    This is a key visual for the dashboard and the judge demo.
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 8))

    if isinstance(shap_values, list):
        # For multi-class, show the HIGH risk class SHAP
        sv = shap_values[-1] if len(shap_values) > 1 else shap_values[0]
    elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        sv = shap_values[:, :, -1]
    else:
        sv = shap_values

    shap.summary_plot(sv, X, feature_names=features,
                      show=False, plot_size=(12, 8))
    path = os.path.join(output_dir, 'shap_summary.png')
    plt.savefig(path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"[Explainer] SHAP summary plot saved to {path}")


def save_shap_bar_plot(shap_values, X: pd.DataFrame,
                        features: list, output_dir: str = 'output/'):
    """
    Save the SHAP mean importance bar chart.
    Shows which features matter most across the entire dataset.
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 7))

    if isinstance(shap_values, list):
        sv = shap_values[-1] if len(shap_values) > 1 else shap_values[0]
    elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        sv = shap_values[:, :, -1]
    else:
        sv = shap_values

    shap.summary_plot(sv, X, feature_names=features,
                      plot_type='bar', show=False, plot_size=(12, 7))
    path = os.path.join(output_dir, 'shap_importance.png')
    plt.savefig(path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"[Explainer] SHAP importance plot saved to {path}")


def run_explainer_pipeline(df: pd.DataFrame, model, X: pd.DataFrame,
                            features: list, output_dir: str = 'output/'):
    """
    Master function — runs SHAP computation, generates all plots,
    and returns the top_risk_factors Series to add to the output CSV.
    """
    explainer, shap_values = compute_shap_values(model, X)
    explanations = generate_explanations(df, shap_values, X, features)
    save_shap_summary_plot(shap_values, X, features, output_dir)
    save_shap_bar_plot(shap_values, X, features, output_dir)
    print(f"[Explainer] Explanations generated for {len(explanations)} customers")
    return explanations
