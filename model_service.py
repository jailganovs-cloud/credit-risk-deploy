"""Load only the project's trusted artifact and return an uncalibrated model score."""
import hashlib
import json
from pathlib import Path

import joblib
import sklearn

from features import validate_record

ROOT = Path(__file__).resolve().parent


class Predictor:
    def __init__(self, root=ROOT):
        root = Path(root)
        self.metadata = json.loads((root / "model_metadata.json").read_text())
        artifact = root / "model.joblib"
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != self.metadata["model_sha256"]:
            raise RuntimeError("The model checksum does not match the recorded release.")
        if sklearn.__version__ != self.metadata["versions"]["scikit-learn"]:
            raise RuntimeError("Use the scikit-learn version pinned in requirements.txt.")
        # A checksum catches accidental drift, not a malicious replacement of both files.
        # Never accept user-uploaded joblib/pickle files.
        self.model = joblib.load(artifact)

    def predict(self, record):
        frame = validate_record(record)
        positive_index = list(self.model.classes_).index(1)
        score = float(self.model.predict_proba(frame)[0, positive_index])
        flag = score >= self.metadata["threshold"]
        return {"model_score": score, "threshold": self.metadata["threshold"],
                "review_flag": "Flagged for review" if flag else "Not flagged for review",
                "score_type": "Uncalibrated class-weighted decision-tree score",
                "use": "Educational demonstration; no credit approval decision"}
