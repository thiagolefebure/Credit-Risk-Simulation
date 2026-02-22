import numpy as np
import pandas as pd
from datetime import date, timedelta
from .config import get_paths

COUNTRIES = ["DK", "SE", "NO", "FI", "PL"]
PRODUCTS = ["TERM", "REVOLVING"]

def _sigmoid(x):
    return 1 / (1 + np.exp(-x))

def generate_synthetic_portfolio(n_loans: int = 30000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    loan_id = [f"L{1000000+i}" for i in range(n_loans)]
    customer_id = [f"C{rng.integers(10000, 999999):06d}" for _ in range(n_loans)]
    country = rng.choice(COUNTRIES, size=n_loans, p=[0.35, 0.2, 0.15, 0.15, 0.15])
    product_type = rng.choice(PRODUCTS, size=n_loans, p=[0.7, 0.3])
    secured = (rng.random(n_loans) < 0.6).astype(int)

    # dates
    base_date = date(2022, 1, 1)
    orig_days = rng.integers(0, 365*3, size=n_loans)
    origination_date = np.array([base_date + timedelta(days=int(d)) for d in orig_days])
    term_years = rng.choice([1,2,3,5,7,10], size=n_loans, p=[0.1,0.15,0.2,0.25,0.15,0.15])
    maturity_date = np.array([od + timedelta(days=int(y*365)) for od, y in zip(origination_date, term_years)])

    # customer characteristics
    age = rng.integers(20, 75, size=n_loans)
    income = rng.lognormal(mean=10.5, sigma=0.45, size=n_loans)  # ~ realistic-ish
    # introduce missingness for DQ
    miss_income = rng.random(n_loans) < 0.015
    income = income.astype(float)
    income[miss_income] = np.nan

    ltv = np.clip(rng.normal(0.65, 0.18, size=n_loans), 0.05, 1.25)
    miss_ltv = rng.random(n_loans) < 0.01
    ltv = ltv.astype(float)
    ltv[miss_ltv] = np.nan

    dti = np.clip(rng.normal(0.35, 0.18, size=n_loans), 0.02, 1.5)
    delinq_12m = rng.poisson(lam=0.25, size=n_loans)
    interest_rate = np.clip(rng.normal(0.045, 0.015, size=n_loans), 0.005, 0.15)

    # exposure
    base_balance = rng.lognormal(mean=10.2, sigma=0.7, size=n_loans)
    balance = np.clip(base_balance, 500, 800000)

    limit_amount = np.where(product_type == "REVOLVING",
                            np.clip(balance * rng.uniform(1.0, 2.5, size=n_loans), 1000, 1000000),
                            0.0)
    undrawn_limit = np.where(product_type == "REVOLVING",
                             np.maximum(limit_amount - balance, 0.0),
                             0.0)

    # Create default flag using a transparent "true" PD generator
    # Macro-ish country effect
    country_effect = np.array([{"DK":-0.15, "SE":-0.10, "NO":-0.12, "FI":-0.05, "PL":0.10}[c] for c in country])
    # Risk drivers
    ltv_f = np.nan_to_num(ltv, nan=0.7)
    income_f = np.nan_to_num(income, nan=np.nanmedian(income))
    score = (
        -4.0
        + 1.8*(ltv_f - 0.6)
        + 1.2*(dti - 0.35)
        + 0.35*delinq_12m
        + 0.8*(1-secured)
        + 0.6*(product_type == "REVOLVING").astype(float)
        - 0.000002*(income_f - np.nanmedian(income))
        + country_effect
    )
    pd_true = _sigmoid(score)
    default_flag = (rng.random(n_loans) < pd_true).astype(int)

    df = pd.DataFrame({
        "loan_id": loan_id,
        "customer_id": customer_id,
        "country": country,
        "product_type": product_type,
        "secured": secured,
        "origination_date": pd.to_datetime(origination_date),
        "maturity_date": pd.to_datetime(maturity_date),
        "balance": balance,
        "limit_amount": limit_amount,
        "undrawn_limit": undrawn_limit,
        "interest_rate": interest_rate,
        "income": income,
        "age": age,
        "ltv": ltv,
        "dti": dti,
        "delinq_12m": delinq_12m,
        "default_flag": default_flag
    })

    # add a small duplicate rate to test uniqueness checks
    if n_loans >= 1000:
        dup_idx = rng.choice(np.arange(n_loans), size=max(3, n_loans//5000), replace=False)
        df = pd.concat([df, df.iloc[dup_idx].copy()], ignore_index=True)

    return df

def main():
    paths = get_paths()
    df = generate_synthetic_portfolio()
    out = paths.synthetic_dir / "loans_synthetic.parquet"
    df.to_parquet(out, index=False)
    print(f"Wrote: {out} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
