"""Export the trained pipeline as transparent JSON for static browser inference."""
import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from features import BILLS, CATEGORICAL, FEATURES, NUMERIC, PAYMENTS, STATUS, example_record

ROOT = Path(__file__).resolve().parent


def export_payload():
    model = joblib.load(ROOT / "model.joblib")
    encoder = model.named_steps["preprocess"].named_transformers_["cat"]
    clf = model.named_steps["model"]
    tree = clf.tree_
    index = list(clf.classes_).index(1)
    # scikit-learn 1.8 predict_proba returns these stored class-weighted values.
    # Preserve them verbatim rather than renormalizing and changing rounding.
    np.testing.assert_allclose(tree.value[:, 0, :].sum(axis=1), 1, rtol=0, atol=1e-10)
    scores = tree.value[:, 0, index]
    return {"format_version": 1, "source_model_sha256": hashlib.sha256((ROOT / "model.joblib").read_bytes()).hexdigest(),
            "features": FEATURES, "numeric": NUMERIC, "categorical": CATEGORICAL,
            "categories": [c.tolist() for c in encoder.categories_],
            "cleaning": {"EDUCATION": {"0": 4, "5": 4, "6": 4}, "MARRIAGE": {"0": 3}},
            "threshold": 0.5, "positive_class": 1, "calibrated": False,
            "tree": {"left": tree.children_left.tolist(), "right": tree.children_right.tolist(),
                     "feature": tree.feature.tolist(), "threshold": tree.threshold.tolist(),
                     "score": scores.tolist()}}


def synthetic_records():
    rng = np.random.default_rng(20)
    records = [example_record(False), example_record(True)]
    for _ in range(126):
        r = example_record()
        r.update(LIMIT_BAL=int(rng.integers(10000, 1000001)), AGE=int(rng.integers(21, 80)),
                 SEX=int(rng.choice([1, 2])), EDUCATION=int(rng.integers(0, 7)), MARRIAGE=int(rng.integers(0, 4)))
        for field in STATUS: r[field] = int(rng.integers(-2, 10))
        for field in BILLS: r[field] = int(rng.integers(-5000, 500001))
        for field in PAYMENTS: r[field] = int(rng.integers(0, 20001))
        records.append(r)
    # Exercise both sides and equality at every numeric tree boundary.
    model = joblib.load(ROOT / "model.joblib")
    names = model.named_steps["preprocess"].get_feature_names_out()
    tree = model.named_steps["model"].tree_
    for feature_index, threshold in zip(tree.feature, tree.threshold):
        if feature_index < 0: continue
        name = str(names[feature_index]).removeprefix("num__")
        if name not in NUMERIC: continue
        if name in STATUS:
            candidates = [int(np.floor(threshold)), int(np.ceil(threshold))]
        else:
            x = np.float32(threshold)
            candidates = [float(np.nextafter(x, np.float32(-np.inf))), float(x), float(np.nextafter(x, np.float32(np.inf)))]
        for value in candidates:
            r = example_record(); r[name] = value; records.append(r)
    return records


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = export_payload()
    model = joblib.load(ROOT / "model.joblib")
    records = synthetic_records()
    scores = model.predict_proba(pd.DataFrame(records, columns=FEATURES))[:, 1]
    fixtures = [{"record": r, "score": float(s)} for r, s in zip(records, scores)]
    if args.check:
        assert json.loads((ROOT / "model.json").read_text()) == payload, "Re-export the changed model."
        assert json.loads((ROOT / "browser_fixtures.json").read_text()) == fixtures, "Regenerate reference fixtures."
        print("Browser export and synthetic reference scores match the Python model.")
    else:
        (ROOT / "model.json").write_text(json.dumps(payload, indent=2) + "\n")
        (ROOT / "browser_fixtures.json").write_text(json.dumps(fixtures, indent=2) + "\n")
        print(f"Exported {len(payload['tree']['left'])} nodes and {len(fixtures)} fictional test cases.")


if __name__ == "__main__": main()
