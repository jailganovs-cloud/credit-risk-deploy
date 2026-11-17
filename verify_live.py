"""Verify deployed static assets without claiming a browser interaction took place."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('url', help='The actual app URL, for example https://jailganovs-credit-risk-demo.hf.space')
args = parser.parse_args()
base = args.url.rstrip('/')
checks = []
for name in ['model.json', 'browser_model.js', 'ui.js', 'examples.json']:
    with urlopen(base+'/'+name, timeout=30) as response: body = response.read()
    local = (ROOT/name).read_bytes()
    if hashlib.sha256(body).digest() != hashlib.sha256(local).digest():
        raise RuntimeError(f'The deployed {name} does not match this local release.')
    checks.append({'file':name, 'matches_local':True})
result = {'url':base, 'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'static_asset_checks':checks, 'browser_interaction_verified':False,
          'next_check':'Open the app and run both fictional examples; capture the actual results.'}
(ROOT/'live_asset_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
