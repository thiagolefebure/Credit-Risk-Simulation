import numpy as np
import pandas as pd

def estimate_ead(df: pd.DataFrame) -> np.ndarray:
    """EAD baseline:
    - TERM: EAD = balance
    - REVOLVING: EAD = balance + CCF * undrawn_limit
      CCF depends on delinquency & product (simple)
    """
    balance = df["balance"].to_numpy()
    undrawn = df["undrawn_limit"].to_numpy()
    is_rev = (df["product_type"] == "REVOLVING").astype(int).to_numpy()
    delinq = df["delinq_12m"].to_numpy()

    ccf = np.clip(0.35 + 0.10*delinq, 0.2, 0.9)
    ead = balance + is_rev * ccf * undrawn
    return ead
