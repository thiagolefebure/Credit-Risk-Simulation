import numpy as np
import pandas as pd

SCENARIOS = {
    "baseline": {"gdp": 0.0, "unemp": 0.0, "rates": 0.0},
    "mild_recession": {"gdp": -1.5, "unemp": 2.0, "rates": 0.5},
    "severe_recession": {"gdp": -3.0, "unemp": 4.0, "rates": 1.5},
}

def stress_pd(pd_base: np.ndarray, scenario: str) -> np.ndarray:
    """Apply a simple macro shock to PD.
    This is NOT a regulatory model; it's a transparent simulation:
      logit(PD_stress) = logit(PD_base) + k1*unemp + k2*rates + k3*gdp
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    s = SCENARIOS[scenario]

    eps = 1e-9
    p = np.clip(pd_base, eps, 1-eps)
    logit = np.log(p/(1-p))

    k_unemp = 0.18
    k_rates = 0.10
    k_gdp = -0.08  # negative gdp increases risk (gdp is negative in recession)

    logit_s = logit + k_unemp*s["unemp"] + k_rates*s["rates"] + k_gdp*s["gdp"]
    pd_s = 1/(1+np.exp(-logit_s))
    return np.clip(pd_s, eps, 1-eps)
