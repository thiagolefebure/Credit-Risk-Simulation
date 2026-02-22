import pandas as pd
import duckdb
from .config import get_paths

def dq_scorecard(df: pd.DataFrame) -> dict:
    total = len(df)
    missing_income = int(df["income"].isna().sum())
    missing_ltv = int(df["ltv"].isna().sum())
    dup_loan_ids = int(df["loan_id"].duplicated().sum())
    invalid_product = int((~df["product_type"].isin(["TERM","REVOLVING"])).sum())
    negative_balance = int((df["balance"] < 0).sum())

    # Simple scoring (0-100)
    penalties = 0.0
    penalties += 35.0 * (missing_income/total)
    penalties += 35.0 * (missing_ltv/total)
    penalties += 20.0 * (dup_loan_ids/total)
    penalties += 30.0 * (invalid_product/total)
    penalties += 30.0 * (negative_balance/total)
    score = max(0.0, 100.0 - penalties)

    return {
        "total_rows": total,
        "missing_income": missing_income,
        "missing_ltv": missing_ltv,
        "duplicate_loan_ids": dup_loan_ids,
        "invalid_product_type": invalid_product,
        "negative_balance": negative_balance,
        "dq_score": float(score)
    }

def load_df() -> pd.DataFrame:
    paths = get_paths()
    p = paths.synthetic_dir / "loans_synthetic.parquet"
    if not p.exists():
        raise FileNotFoundError("Synthetic dataset not found. Run: python -m src.crsim.generate_data")
    return pd.read_parquet(p)

def main():
    df = load_df()
    sc = dq_scorecard(df)
    print("DQ scorecard:")
    for k, v in sc.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
