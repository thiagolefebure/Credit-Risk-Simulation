import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.calibration import calibration_curve

def train_pd_model(X: pd.DataFrame, y: pd.Series, seed: int = 42):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)

    model = LogisticRegression(max_iter=2000, n_jobs=None)
    model.fit(X_train, y_train)

    proba_test = model.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba_test)

    frac_pos, mean_pred = calibration_curve(y_test, proba_test, n_bins=10, strategy="quantile")

    return {
        "model": model,
        "auc": float(auc),
        "calibration": {
            "fraction_of_positives": frac_pos.tolist(),
            "mean_predicted_value": mean_pred.tolist(),
        }
    }

def score_pd(model, X: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(X)[:,1]
