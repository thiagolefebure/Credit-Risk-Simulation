import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()

    # Impute missing values (simple + transparent)
    df["income"] = df["income"].fillna(df["income"].median())
    df["ltv"] = df["ltv"].fillna(df["ltv"].median())

    # Encode categorical variables
    df["is_revolving"] = (df["product_type"] == "REVOLVING").astype(int)
    df["is_secured"] = df["secured"].astype(int)

    country_dummies = pd.get_dummies(df["country"], prefix="cty", drop_first=True)
    X = pd.concat([
        df[["age","income","ltv","dti","delinq_12m","interest_rate","is_revolving","is_secured","balance"]],
        country_dummies
    ], axis=1)

    y = df["default_flag"].astype(int)
    return X, y
