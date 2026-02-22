import json
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import get_paths
from .generate_data import generate_synthetic_portfolio
from .features import build_features
from .pd_model import train_pd_model, score_pd
from .lgd_model import estimate_lgd
from .ead_model import estimate_ead
from .el_ul import expected_loss, portfolio_metrics
from .stress import SCENARIOS, stress_pd
from .dq_checks import dq_scorecard
from .lineage import basic_lineage

def _save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)

def ensure_data():
    paths = get_paths()
    p = paths.synthetic_dir / "loans_synthetic.parquet"
    if not p.exists():
        df = generate_synthetic_portfolio()
        df.to_parquet(p, index=False)
    return p

def load_to_duckdb(parquet_path: Path):
    con = duckdb.connect(database=":memory:")
    paths = get_paths()
    schema_sql = (paths.sql_dir / "schema.sql").read_text(encoding="utf-8")
    con.execute(schema_sql)

    df = pd.read_parquet(parquet_path)
    con.register("df", df)
    con.execute("INSERT INTO loans_raw SELECT * FROM df")
    # transformations
    con.execute((paths.sql_dir / "transformations.sql").read_text(encoding="utf-8"))
    return con

def build_reports():
    paths = get_paths()
    parquet_path = ensure_data()
    df = pd.read_parquet(parquet_path)

    # DQ
    dq = dq_scorecard(df)

    # Train PD model
    X, y = build_features(df)
    trained = train_pd_model(X, y)
    model = trained["model"]
    pd_hat = score_pd(model, X)

    # LGD / EAD / EL
    lgd = estimate_lgd(df)
    ead = estimate_ead(df)
    el = expected_loss(pd_hat, lgd, ead)

    # Stress scenarios
    stress_rows = []
    for name in SCENARIOS.keys():
        pd_s = stress_pd(pd_hat, name)
        el_s = expected_loss(pd_s, lgd, ead)
        m = portfolio_metrics(el_s)
        m["scenario"] = name
        stress_rows.append(m)
    stress_df = pd.DataFrame(stress_rows).sort_values("scenario")

    # Segment breakdown
    out = df.copy()
    out["pd"] = pd_hat
    out["lgd"] = lgd
    out["ead"] = ead
    out["el"] = el
    out["pd_band"] = pd.cut(out["pd"], bins=[0,0.01,0.03,0.06,0.10,1.0], labels=["<1%","1-3%","3-6%","6-10%",">10%"], include_lowest=True)

    seg = (out
           .groupby(["country","product_type","pd_band"], dropna=False)
           .agg(loans=("loan_id","count"),
                ead_total=("ead","sum"),
                el_total=("el","sum"),
                pd_mean=("pd","mean"),
                lgd_mean=("lgd","mean"))
           .reset_index()
          )

    # Figures
    fig1 = plt.figure()
    plt.hist(out["pd"], bins=40)
    plt.title("Distribution of predicted PD")
    plt.xlabel("PD")
    plt.ylabel("Loans")
    _save_fig(fig1, paths.figures_dir / "pd_distribution.png")

    fig2 = plt.figure()
    plt.plot(trained["calibration"]["mean_predicted_value"], trained["calibration"]["fraction_of_positives"], marker="o")
    plt.plot([0,1],[0,1], linestyle="--")
    plt.title("PD Calibration (quantile bins)")
    plt.xlabel("Mean predicted PD")
    plt.ylabel("Observed default rate")
    _save_fig(fig2, paths.figures_dir / "pd_calibration.png")

    fig3 = plt.figure()
    plt.plot(stress_df["scenario"], stress_df["EL_total"], marker="o")
    plt.title("Expected Loss by scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Total EL")
    plt.xticks(rotation=20)
    _save_fig(fig3, paths.figures_dir / "el_by_scenario.png")

    # Render HTML reports
    env = Environment(
        loader=FileSystemLoader(str(paths.root / "src" / "crsim" / "templates")),
        autoescape=select_autoescape(["html"])
    )

    risk_t = env.get_template("risk_report.html.j2")
    dq_t = env.get_template("dq_report.html.j2")

    portfolio = portfolio_metrics(el)
    lineage = basic_lineage()

    risk_html = risk_t.render(
        generated_at=str(pd.Timestamp.utcnow()),
        auc=trained["auc"],
        portfolio=portfolio,
        stress=stress_df.to_dict(orient="records"),
        seg_table=seg.sort_values("el_total", ascending=False).head(25).to_dict(orient="records"),
        figures={
            "pd_distribution": "figures/pd_distribution.png",
            "pd_calibration": "figures/pd_calibration.png",
            "el_by_scenario": "figures/el_by_scenario.png"
        },
        lineage=lineage
    )

    dq_html = dq_t.render(
        generated_at=str(pd.Timestamp.utcnow()),
        dq=dq,
        top_issues=_top_issues(dq)
    )

    (paths.reports_dir / "risk_report.html").write_text(risk_html, encoding="utf-8")
    (paths.reports_dir / "dq_report.html").write_text(dq_html, encoding="utf-8")

    # Save a small artifacts JSON
    artifacts = {
        "auc": trained["auc"],
        "portfolio": portfolio,
        "dq": dq,
        "stress": stress_df.to_dict(orient="records")
    }
    (paths.reports_dir / "artifacts.json").write_text(json.dumps(artifacts, indent=2), encoding="utf-8")

    return paths

def _top_issues(dq: dict) -> list[dict]:
    issues = []
    if dq["duplicate_loan_ids"] > 0:
        issues.append({"issue":"Duplicate loan_id", "count": dq["duplicate_loan_ids"], "action":"Investigate upstream key generation; enforce uniqueness constraints."})
    if dq["missing_income"] > 0:
        issues.append({"issue":"Missing income", "count": dq["missing_income"], "action":"Define imputation rules; validate source completeness; add control checks."})
    if dq["missing_ltv"] > 0:
        issues.append({"issue":"Missing LTV", "count": dq["missing_ltv"], "action":"Backfill from collateral systems; enforce mandatory field for secured loans."})
    if dq["invalid_product_type"] > 0:
        issues.append({"issue":"Invalid product_type", "count": dq["invalid_product_type"], "action":"Apply domain constraints; map legacy codes to standard taxonomy."})
    if dq["negative_balance"] > 0:
        issues.append({"issue":"Negative balance", "count": dq["negative_balance"], "action":"Reconcile accounting postings; validate sign conventions and currency conversions."})
    if not issues:
        issues.append({"issue":"No critical issues detected", "count": 0, "action":"Maintain monitoring; review thresholds periodically."})
    return issues[:8]

def main():
    paths = build_reports()
    print("Done.")
    print(f"Open: {paths.reports_dir / 'risk_report.html'}")
    print(f"Open: {paths.reports_dir / 'dq_report.html'}")

if __name__ == "__main__":
    main()
