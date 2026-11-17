"""Shared raw-input contract and Module 8 category cleaning."""
import math

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

CATEGORICAL = ["SEX", "EDUCATION", "MARRIAGE"]
STATUS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYMENTS = [f"PAY_AMT{i}" for i in range(1, 7)]
FEATURES = ["LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"] + STATUS + BILLS + PAYMENTS
NUMERIC = [name for name in FEATURES if name not in CATEGORICAL]


class FeatureCleaner(TransformerMixin, BaseEstimator):
    """Keep cleaning inside the serialized pipeline, shared by training and serving."""

    def fit(self, X, y=None):
        self.feature_names_in_ = X.columns.to_numpy()
        self.n_features_in_ = len(X.columns)
        return self

    def transform(self, X):
        result = X.loc[:, FEATURES].copy()
        result["EDUCATION"] = result["EDUCATION"].replace({0: 4, 5: 4, 6: 4})
        result["MARRIAGE"] = result["MARRIAGE"].replace({0: 3})
        return result


def validate_record(record):
    missing = sorted(set(FEATURES) - set(record))
    extra = sorted(set(record) - set(FEATURES))
    if missing or extra:
        raise ValueError(f"Input fields do not match. Missing: {missing}; unexpected: {extra}")
    values = {}
    for name in FEATURES:
        item = record[name]
        if item is None or isinstance(item, bool):
            raise ValueError(f"{name} must be a finite number.")
        try:
            value = float(item)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"{name} must be a finite number.") from error
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
        values[name] = value
    codes = {"SEX": {1, 2}, "EDUCATION": set(range(7)), "MARRIAGE": {0, 1, 2, 3}}
    codes.update({name: set(range(-2, 10)) for name in STATUS})
    for name, allowed in codes.items():
        if values[name] not in allowed:
            raise ValueError(f"{name} has an unsupported category code.")
        values[name] = int(values[name])
    if values["LIMIT_BAL"] <= 0:
        raise ValueError("Credit limit must be greater than zero.")
    if not 18 <= values["AGE"] <= 100 or not values["AGE"].is_integer():
        raise ValueError("Age must be an integer from 18 to 100 for this demo.")
    if any(values[name] < 0 for name in PAYMENTS):
        raise ValueError("Previous payment amounts cannot be negative.")
    return pd.DataFrame([values], columns=FEATURES)


def example_record(delayed=False):
    """Constructed demo input, not a row copied from a customer dataset."""
    return dict(zip(FEATURES, [200000, 2, 2, 1, 35] +
                    ([2, 2, 1, 0, 0, 0] if delayed else [0] * 6) +
                    [50000, 45000, 40000, 35000, 30000, 25000] + [5000] * 6))
