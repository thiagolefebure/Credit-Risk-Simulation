# Credit Risk Simulation (PD / LGD / EAD) + Data Quality (BCBS239 mindset)

This repository demonstrates an end-to-end **credit risk analytics** workflow on a **synthetic** portfolio:
- Generate a loan-level dataset (reproducible)
- Train a **PD** model (logistic regression) and evaluate AUC + calibration
- Estimate **LGD** and **EAD** using transparent baselines
- Compute **Expected Loss (EL = PD × LGD × EAD)**
- Run **macro stress scenarios** (baseline / mild / severe)
- Add **Data Quality controls** (completeness, uniqueness, validity) and a DQ scorecard
- Produce management-ready **HTML reports** (risk + DQ) with figures

> Disclaimer: This is a transparent simulation for portfolio analytics & data governance demonstration. It is **not** a regulatory IRB model.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run end-to-end (generates data + reports)
python -m src.crsim.report
```

Outputs:
- `reports/risk_report.html`
- `reports/dq_report.html`
- figures in `reports/figures/`

## What this showcases (aligned with Nordea role)
- Root-cause mindset for data issues + reconciliation checks
- Data governance framing (critical elements, controls, lineage-light)
- Analytical tooling and reporting for stakeholders
- Scenario thinking (stress testing) and structured deliveries

## Repo structure
- `src/crsim/` : core Python modules
- `sql/` : optional DuckDB schema + transformations + DQ query examples
- `reports/` : generated HTML reports
- `data/synthetic/` : generated synthetic dataset (parquet)

## Suggested extension ideas
- Replace LGD baseline with beta regression
- Add scorecards by portfolio segments (rating, country, product)
- Add monitoring (PSI / drift) and model versioning
