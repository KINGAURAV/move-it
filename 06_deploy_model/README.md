# 🚀 Step 6 — Deploy Model

**Move-It** › **Vayu Model Serving** · `06_deploy_model/`

| [← Previous — Step 5 — Model Registry](../05_model_registry/) | [Next — Step 7 — Build App →](../07_build_app/) |
|:---|---:|

Deploy **`04_starter-kit/model.joblib`** for **online sklearn inference** via **Vayu Model Serving**.

---

<details>
<summary><h3>🧩 What's in this step?</h3></summary>

Deploy the trained sklearn `Pipeline` so the [Step 7 Streamlit UI](../07_build_app/) can call a **predict HTTP endpoint** (not local `joblib` loading).

</details>

---

<details>
<summary><h3>📋 Prerequisites</h3></summary>

- [Step 4 — Starter Kit](../04_starter-kit/) — `model.joblib` and `category_labels.json` generated
- [Step 5 — Vayu Model Registry](../05_model_registry/) — artifact registered

</details>

---

<details>
<summary><h3>🚀 Deploy in Vayu Model Serving</h3></summary>

1. **Confirm artifact** — `04_starter-kit/model.joblib` exists.
2. **Register** via [Step 5](../05_model_registry/) if not already done.
3. **Create deployment** in Vayu Model Serving:
   - Model Type: **PredictiveAI**
   - Framework: **sklearn**
   - **Model and version:** Select the model and version you registered in [Step 5](../05_model_registry/).
   - **Compute and storage:** Choose compute and storage resources appropriate for your `model.joblib` size.
   - **Storage type:** Select **Dedicated**.
4. **Note the predict endpoint** when the deployment is **Ready**. The Vayu UI typically copies only the base URL through `/v1` (for example, `http://<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1`). Append `/models/<MODEL_NAME>:predict` to form the full predict URL:

   `http://<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models/<MODEL_NAME>:predict`

   For sidebar configuration in [Step 7](../07_build_app/), see **Launch the realtime pipeline** in the [Move-It overview](../README.md).

**Test with curl:**

First, query the `/v1/models` endpoint to list all available models. Most OpenAI-compatible inference servers expose this endpoint.

```bash
curl -X GET "<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models"
```

Sample output `{"models":["model"]}` — the id here is `model`.

```bash
curl -X POST \
  "https://<PRIVATE_OR_PUBLIC_ENDPOINT_FROM_MODEL_SERVING_UI>/v1/models/<MODEL_ID>:predict" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      "worldcom ex-boss launches defence lawyers defending the former worldcom chief executive argued that he was not responsible for the company collapse."
    ]
  }'
```

Example response: `{"predictions": [0]}` — map codes via `category_labels.json` or the table in the [Move-It overview](../README.md).

Note: `instances` should be changed based on the use case.

</details>

---

<details>
<summary><h3>💡 Pro tips and notes</h3></summary>

- **Model name** — must match between the Vayu deployment, predict URL path, and Streamlit sidebar.
- **Retrain** — re-run `train_model.ipynb` and redeploy after notebook changes.

</details>

---

| [← Previous — Step 5 — Model Registry](../05_model_registry/) | [Overview](../README.md) | [Next — Step 7 — Build App →](../07_build_app/) |
|:---|:---:|---:|
