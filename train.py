"""Reconstruct the Module 8 tuned tree from the original UCI workbook."""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from features import CATEGORICAL, FEATURES, NUMERIC, FeatureCleaner, example_record

ROOT = Path(__file__).resolve().parent
TARGET = "default payment next month"


def pipeline(**params):
    return Pipeline([
        ("clean", FeatureCleaner()),
        ("preprocess", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC)])),
        ("model", DecisionTreeClassifier(random_state=20, **params))])


def evaluate(model, X, y):
    labels = model.predict(X)
    scores = model.predict_proba(X)[:, list(model.classes_).index(1)]
    tn, fp, fn, tp = confusion_matrix(y, labels, labels=[0, 1]).ravel()
    return {"accuracy": accuracy_score(y, labels), "precision": precision_score(y, labels),
            "recall": recall_score(y, labels), "f1": f1_score(y, labels),
            "roc_auc": roc_auc_score(y, scores),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--tune", action="store_true", help="Repeat the 40 candidate CV search")
    args = parser.parse_args()
    df = pd.read_excel(args.data, header=1, engine="xlrd")
    if len(df) != 30000 or set(FEATURES + ["ID", TARGET]) != set(df.columns):
        raise ValueError("Expected the original 30,000-row UCI credit-card workbook.")
    X, y = df[FEATURES], df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=20)
    baseline = pipeline(max_depth=4).fit(X_train, y_train)
    start = time.perf_counter()
    cv_score = None
    if args.tune:
        search = GridSearchCV(pipeline(), {
            "model__max_depth": [3, 4, 5, 7, 10],
            "model__min_samples_leaf": [1, 10, 30, 60],
            "model__class_weight": [None, "balanced"]}, scoring="f1",
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=20), n_jobs=1)
        search.fit(X_train, y_train)
        model = search.best_estimator_
        cv_score = float(search.best_score_)
        pd.DataFrame(search.cv_results_).to_csv(ROOT / "cv_results.csv", index=False)
    else:
        model = pipeline(max_depth=4, min_samples_leaf=30, class_weight="balanced")
        model.fit(X_train, y_train)
    elapsed = time.perf_counter() - start
    before = model.predict_proba(X_test)
    joblib.dump(model, ROOT / "model.joblib", compress=3)
    restored = joblib.load(ROOT / "model.joblib")
    after = restored.predict_proba(X_test)
    np.testing.assert_array_equal(before, after)
    clf = model.named_steps["model"]
    metadata = {
        "model": "Module 8 tuned decision tree reconstruction", "threshold": 0.5,
        "positive_class": "default on next payment", "features": FEATURES,
        "parameters": {k: clf.get_params()[k] for k in ["max_depth", "min_samples_leaf", "class_weight", "random_state"]},
        "source": "Yeh (2009), UCI Default of Credit Card Clients, DOI 10.24432/C55S3H",
        "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "model_sha256": hashlib.sha256((ROOT / "model.joblib").read_bytes()).hexdigest(),
        "train_rows": len(X_train), "test_rows": len(X_test),
        "test_defaults": int(y_test.sum()), "split_seed": 20,
        "baseline_holdout": evaluate(baseline, X_test, y_test),
        "tuned_holdout": evaluate(model, X_test, y_test), "cv_f1": cv_score,
        "search_or_fit_seconds": elapsed, "serialization_equal_rows": len(X_test),
        "versions": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                     "pandas": pd.__version__, "numpy": np.__version__,
                     "scipy": scipy.__version__, "joblib": joblib.__version__},
        "remote_space_verified": False, "github_actions_verified": False,
        "provenance": "Recreated from source data and Module 8 settings; original serialized artifact was not supplied.",
        "calibrated": False}
    (ROOT / "model_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    examples = []
    for delayed in [False, True]:
        record = example_record(delayed)
        score = float(model.predict_proba(pd.DataFrame([record], columns=FEATURES))[0, 1])
        examples.append({"name": "Recent delays" if delayed else "No recorded delays",
                         "record": record, "expected_model_score": score})
    (ROOT / "examples.json").write_text(json.dumps(examples, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
