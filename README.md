# Smart KYC Risk Scoring Engine

> AI-powered KYC (Know Your Customer) Risk Scoring Engine for automated customer onboarding decisions in financial institutions.

**BNY Hackathon 2026 · We Tried Team**

---

## What It Does

This system takes raw customer data (1,000 records × 15 features) and produces:
- A **weighted risk score** (0–100) for every customer
- A **risk tier** (LOW / MEDIUM / HIGH) via ML classification
- An **onboarding decision** (APPROVE / MANUAL_REVIEW / REJECT / EDD)
- **Plain-English explanations** for every flagged customer (SHAP-powered)
- An **interactive dashboard** for compliance officers

## Architecture

```
kyc_industry_dataset.csv
        ↓
  Preprocessing → Feature Engineering (8 composite features)
        ↓
  Weighted Risk Scoring (13 features, weights sum to 100)
        ↓
  ML Classification (3 models compared: LogReg / RF / XGBoost)
        ↓
  SHAP Explainability (top 3 risk factors per customer)
        ↓
  kyc_output.csv + Streamlit Dashboard
```

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python main.py

# 4. Launch the dashboard
streamlit run dashboard.py
```

## Project Structure

```
kyc-engine/
├── data/
│   └── kyc_industry_dataset.csv      ← provided dataset
├── output/
│   ├── kyc_output.csv                ← generated results
│   ├── shap_summary.png             ← SHAP beeswarm plot
│   └── shap_importance.png          ← SHAP feature importance
├── src/
│   ├── __init__.py
│   ├── preprocessor.py              ← data cleaning + encoding
│   ├── feature_engineer.py          ← 8 composite features
│   ├── scorer.py                    ← weighted risk scoring
│   ├── model.py                     ← 3-model comparison + XGBoost
│   └── explainer.py                 ← SHAP explainability
├── main.py                          ← pipeline orchestrator
├── dashboard.py                     ← Streamlit dashboard
├── requirements.txt                 ← dependencies
└── README.md                        ← this file
```

## Key Design Decisions

### Weight Justification (Risk Score)
| Feature | Weight | Tier | Rationale |
|---|---|---|---|
| sanctions_flag | 25 | CRITICAL | Regulatory mandate — missing one = massive fine |
| fraud_history_flag | 20 | CRITICAL | 52% prevalence — strongest predictor |
| pep_flag | 12 | HIGH | Politically exposed persons always need review |
| adverse_media_flag | 8 | HIGH | Reputational + fraud risk |
| document_status | 8 | HIGH | Identity verification failure |
| country_risk | 7 | MEDIUM | Standard AML geography signal |
| digital_risk_score | 6 | MEDIUM | Digital banking fraud detection |
| address_verified | 5 | MEDIUM | Fraud indicator |
| txn_income_ratio | 3 | LOW | Behavioural mismatch |
| age_risk_group | 2 | LOW | Edge group uplift |
| high_risk_occupation | 2 | LOW | Cash business uplift |
| complex_account | 1 | LOW | Corporate/NRI uplift |
| is_new_customer | 1 | LOW | No baseline |

### Sanctions Hard Rule
`sanctions_flag = 1` → force score ≥ 85 → always HIGH tier → always EDD decision.
No sanctioned customer can ever be auto-approved regardless of other signals.

### ML + Rule Hybrid
If EITHER the weighted scoring formula OR the ML model classifies a customer as HIGH risk, the final tier is HIGH. Safety first.

## Innovation Highlights

1. **8 Engineered Features** — including income-occupation anomaly detection
2. **3-Model Comparison** — LogReg, Random Forest, XGBoost evaluated and compared
3. **SHAP Explainability** — every flagged customer gets top 3 reasons in plain English
4. **Business Insights** — acquisition channel risk analysis, red flag combinations dashboard

## Technology Stack

- Python 3.9+ · pandas · NumPy · scikit-learn
- XGBoost · SHAP · imbalanced-learn (SMOTE)
- Streamlit · Plotly · Matplotlib · Seaborn

## License

Built for BNY Hackathon 2026. Synthetic data only — no real customer PII used.
All libraries are open-source (MIT/BSD/Apache licensed).
