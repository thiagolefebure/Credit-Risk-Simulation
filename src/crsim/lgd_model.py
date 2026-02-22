import numpy as np
import pandas as pd

def estimate_lgd(df: pd.DataFrame) -> np.ndarray:
    """Simple but plausible LGD baseline:
    - Secured loans lower LGD
    - Higher LTV -> higher LGD
    - Revolving slightly higher LGD
    Output clipped to [0.05, 0.95]
    """
    ltv = df["ltv"].fillna(df["ltv"].median()).to_numpy()
    secured = df["secured"].to_numpy()
    is_rev = (df["product_type"] == "REVOLVING").astype(int).to_numpy()

    base = 0.35 + 0.25*(ltv - 0.6) + 0.05*is_rev - 0.12*secured
    lgd = np.clip(base, 0.05, 0.95)
    return lgd
