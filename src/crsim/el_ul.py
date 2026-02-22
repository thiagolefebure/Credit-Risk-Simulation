import numpy as np

def expected_loss(pd: np.ndarray, lgd: np.ndarray, ead: np.ndarray) -> np.ndarray:
    return pd * lgd * ead

def portfolio_metrics(el: np.ndarray) -> dict:
    # UL proxy: std dev of EL (not regulatory capital, just illustrative)
    return {
        "EL_total": float(el.sum()),
        "EL_mean": float(el.mean()),
        "EL_p95": float(np.quantile(el, 0.95)),
        "EL_std": float(el.std(ddof=1)) if len(el) > 1 else 0.0
    }
