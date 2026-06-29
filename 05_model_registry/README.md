# Step 5 — Model Registry

**Move-It** › **Vayu Model Registry** · `05_model_registry/`

| | |
|---|---|
| **⬅ Previous** | [Step 4 — Starter Kit](../04_starter-kit/) |
| **Next ➡**     | [Step 6 — Deploy Model →](../06_deploy_model/) |

Upload your trained `model.joblib` from [Step 4](../04_starter-kit/) to **Vayu Object Storage**, then register it in the **Vayu Model Registry** so it can be deployed via Model Serving.

---

## Open Model Registry

Go to [Vayu Model Registry](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-registry-list).

For the full registration wizard (Start → Model Configuration → Object Storage → Review), see the [Model Registry documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-registry/).

---

## Folder Contents

| File | Purpose |
|------|---------|
| `upload_model.py` | Upload `04_starter-kit/model.joblib` to S3 |

---

## Quick Start

### 1. Upload `model.joblib` to S3

Ensure your project root [`.env`](../README.md) includes the S3 variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, `S3_BUCKET_NAME`, and `S3_MODEL_KEY`). Then run:

```bash
python 05_model_registry/upload_model.py
```

[`upload_model.py`](upload_model.py) reads `S3_MODEL_KEY` from `.env` (default: `move-it/model.joblib`). Change that value in `.env` if your team uses a different object path.

### 2. Register the model

On the [Vayu Model Registry](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-registry-list) page. Follow the [Model Registry documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-registry/) for step-by-step wizard details:

1. **Register** a new model.
2. **Framework:** Select **sklearn**.
3. **Metadata:** Add `algorithm: logistic_regression` (and any other tags your team needs).
4. **S3 credentials and prefix:** Configure the same S3 access from your `.env`. For the **prefix**, use only the folder path where the `.joblib` file lives — not the filename itself.

   | `S3_MODEL_KEY` in `.env` | Prefix to enter |
   |--------------------------|-----------------|
   | `move-it/model.joblib` | `move-it` |

5. **Verify:** Confirm the registered model appears in the registry and is ready for deployment.

---

## Navigation

| | |
|---|---|
| **⬅ Previous** | [Step 4 — Starter Kit](../04_starter-kit/) |
| **Next ➡**     | [Step 6 — Deploy Model →](../06_deploy_model/) |
| **🏠 Overview** | [Move-It overview](../README.md) |
