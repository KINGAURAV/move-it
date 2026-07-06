# Step 6 — Deploy Model

**Move-It** › **Vayu Model Serving** · `06_deploy_model/`

Deploy **`04_starter_kit/model.joblib`** for **online sklearn inference** via **Vayu Model Serving**.

---

## Quick Navigation

|        |        |
|--------|--------|
| **⬅ Previous** | [Step 4 — Vayu Model Registry](../05_model_registry/) |
| **Next ➡**     | [Step 6 — Vayu inference UI](../07_build_app/) |

---

## What's In This Step?

Deploy the trained sklearn `Pipeline` so the [Step 7 Streamlit UI](../07_build_app/) can call a **predict HTTP endpoint** (not local `joblib` loading).

---

## Prerequisites

- ✅ [Step 3 — Vayu training](../04_starter_kit/) — `model.joblib` and `category_labels.json` generated
- ✅ [Step 4 — Vayu Model Registry](../05_model_registry/) — artifact registered

---

## Deploy in Vayu Model Serving

1. **Confirm artifact** — `03_starter_kit/model.joblib` exists.
2. **Register** via [Step 4](../05_model_registry/) if not already done.
3. **Create deployment** in Vayu Model Serving:
   - Model Type: **PredictiveAI**
   - Framework: **sklearn**
   - Model and version : select from the dropdown 
   - compute and storage : select resources based on model size 
   - Storage Type: select dedicated
4. **Copy predict URL** when the endpoint is ready (V1 example):

   `http://<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models/<MODEL_NAME>:predict`

5. Continue to [Step 6 — Vayu inference UI](../07_build_app/) and paste host + model name in the Streamlit sidebar.

  **Test with curl:**

  ```bash

  Step 1: Get the available model ID

  First, query the /v1/models endpoint to list all available models. Most OpenAI-compatible inference servers expose this endpoint.

  curl -X GET  "<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models"

  sample output {"models":["model"]} and the id here is "model"


  curl -X POST \
  "https://<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models/<MODEL_ID>:predict" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      "worldcom ex-boss launches defence lawyers defending the former worldcom chief executive argued that he was not responsible for the company collapse." 
    ]
  }'
Example response: `{"predictions": [0]}` — map codes via `category_labels.json` or the table in [Move-It overview](../README.md).
Note : instances should be changed based on usecase

## Pro Tips & Notes

- **Model name** — must match between the Vayu deployment, predict URL path, and Streamlit sidebar.
- **Retrain** — re-run `train.ipynb` and redeploy after notebook changes.

---

## Jump Around

|        |        |
|--------|--------|
| **⬅ Previous** | [Step 5 — Vayu Model Registry](../05_model_registry/) |
| **Next ➡**     | [Step 7 — Vayu inference UI](../07_build_app/) |
| **🏠 Overview**| [Predict-It overview](../README.md) |
 