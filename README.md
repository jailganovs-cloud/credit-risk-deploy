---
title: Credit Risk Model Demonstration
emoji: 📊
colorFrom: blue
colorTo: gray
sdk: static
app_file: index.html
pinned: false
---

# Credit risk model deployment

This free Static Space runs the Module 8 tuned decision tree in the visitor's
browser. It does not require Gradio, Docker, paid compute, or a prediction API.
The trained tree is exported from the reconstructed scikit-learn pipeline to
`model.json`. `browser_model.js` preserves category cleaning, encoding, numeric
float32 conversion, tree traversal, and the class-weighted leaf score.

The account's Create Space screen showed Gradio and Docker as **Paid**, so the
submission uses the free Static SDK. The source assignment permits a Hugging Face
Space and requires avoiding costs; it does not specify a mandatory SDK.

## Run locally

Python 3 is needed only to serve the static files:

```bash
python -m http.server 8000
```

Open http://localhost:8000 in a modern browser. The deployed app uses HTML,
JavaScript, and JSON only. No package installation or model training is needed
to use it. Form values remain in browser memory; they are not stored locally or
submitted to a prediction backend. Ordinary hosting request metadata may exist.

## Verify or reproduce the model export

Use Python 3.12 and Node.js 22 or newer:

```bash
pip install -r requirements.txt
python export_browser.py --check
node --test test_browser.mjs
```

`--check` ensures that `model.json` and the 165 fictional and boundary fixtures
correspond to the approved Python artifact. No npm packages are required.
For a fresh export, run `python export_browser.py` without `--check`.

To reconstruct the model and repeat the holdout comparison, obtain the original
UCI XLS workbook from https://doi.org/10.24432/C55S3H and keep it outside the repo:

```bash
pip install -r requirements-training.txt
python train.py --data /path/to/source.xls --tune
python export_browser.py
python verify_export.py --data /path/to/source.xls
```

The 6,000-row holdout comparison verifies equivalence to the historical model.
It is not a new independent generalization experiment. Raw test records are not
included in the deployment package. See `local_verification.json` for actual local
comparison results and `model_metadata.json` for the original reconstruction.

## Deploy through GitHub Actions

1. Create a Hugging Face Space named `credit-risk-demo` under `jailganovs`.
   Choose **Static → Blank → Public → Create Space**. No subscription is needed.
2. Create a GitHub repository with default branch `main`. Upload all project
   files, including `.github/workflows/deploy.yml`. Upload the extracted files,
   not this ZIP and not the source XLS workbook.
3. Create a fine-grained Hugging Face access token with write access to this
   Space. In GitHub repository Settings → Secrets and variables → Actions →
   Secrets, add it as **HF_TOKEN**. Never paste tokens into chat or source code.
4. Under Actions → Variables, create **HF_SPACE** with value
   **jailganovs/credit-risk-demo**.
5. In the Actions tab run **Test and deploy credit risk demo** on `main`.
   The Python export check and seven JavaScript tests must pass before syncing.
6. Open https://huggingface.co/spaces/jailganovs/credit-risk-demo after the
   deployment finishes. Run both fictional examples in the actual browser.
   Expected scores are approximately **0.2487** and **0.8751**.
7. Change one visible phrase in `index.html`, commit to main, and verify that a
   second workflow updates the running Space. Save the commit and run links.

After the real app URL is available, the optional script checks deployed assets:

```bash
python verify_live.py https://jailganovs-credit-risk-demo.hf.space
```

This checks assets, not browser interaction. A user must still exercise both
examples and confirm the visible output. No live deployment or GitHub workflow
has been verified during local preparation.

## Interpretation

The score is an uncalibrated class-weighted tree output, not a validated default
probability. Scores at least 0.50 produce a review flag. No approval decision is
made. The historical Taiwan dataset covers 2005 and contains demographic inputs;
it does not establish suitability for modern lending or another population.

Static deployment exposes the exported model and inference code publicly. It
provides no authenticated backend, centralized prediction logging, private model
storage, traffic controls, or availability commitment.

## References

- Yeh, I. (2009). Default of Credit Card Clients. UCI. https://doi.org/10.24432/C55S3H. CC BY 4.0.
- https://huggingface.co/docs/hub/spaces-sdks-static
- https://huggingface.co/docs/hub/spaces-github-actions
- https://scikit-learn.org/stable/model_persistence.html
