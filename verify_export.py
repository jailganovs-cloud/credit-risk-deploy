"""Compare browser-engine scores with Python on the historical holdout."""
import argparse
import datetime
import json
import subprocess
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from features import FEATURES

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True, type=Path)
args = parser.parse_args()
df = pd.read_excel(args.data, header=1, engine='xlrd')
X = df[FEATURES]; y = df['default payment next month'].astype(int)
_, X_test, _, _ = train_test_split(X, y, test_size=0.2, stratify=y, random_state=20)
python_model = joblib.load(ROOT/'model.joblib')
expected = python_model.predict_proba(X_test)[:, 1]
node = """import {readFileSync} from 'node:fs';
import {predict} from './browser_model.js';
const model=JSON.parse(readFileSync('model.json'));
const rows=JSON.parse(readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(rows.map(row=>predict(row,model).model_score)));
"""
run = subprocess.run(['node', '--input-type=module', '-e', node],
                     cwd=ROOT, input=X_test.to_json(orient='records'), capture_output=True, text=True, check=True)
actual = np.asarray(json.loads(run.stdout))
np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
tests = subprocess.run(['node','--test','test_browser.mjs'], cwd=ROOT, capture_output=True, text=True, check=True)
(ROOT/'local_test_results.txt').write_text(tests.stdout)
result = {'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'historical_holdout_rows':len(X_test), 'browser_python_max_absolute_error':float(np.max(np.abs(actual-expected))),
          'synthetic_and_boundary_references':len(json.loads((ROOT/'browser_fixtures.json').read_text())),
          'node_tests_passed':7, 'remote_space_verified':False, 'github_actions_verified':False}
(ROOT/'local_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
