# Step 6 — Deploy Model

**Move-It** › **Vayu Model Serving** · `06_deploy_model/`

| | |
|---|---|
| **⬅ Previous** | [Step 5 — Model Registry](../05_model_registry/) |
| **Next ➡**     | [Step 7 — Build App →](../07_build_app/) |

Deploy your registered model with **Vayu Model Serving** to create a production-ready REST endpoint for irrigation prediction.

---

## Open Model Serving

Go to [Vayu Model Serving](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-serving-list).

For the full create wizard (Start → Infrastructure → Predictor Configuration → Configure Compute and Storage → Review), see the [Model Serving documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/).

---

## Quick Start

1. **Create a deployment:** On the [Vayu Model Serving](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-serving-list) page, start a new deployment. Follow the [Model Serving documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/) for step-by-step wizard details.
2. **Select Predictive AI:** Choose **Predictive AI** as the serving type.
3. **Predictor config:** Select the model and version you registered in [Step 5](../05_model_registry/).
4. **Deploy:** Submit the deployment and wait for the **Ready** status.
5. **Test:** Use the provided predict URL (e.g., `https://<url>/v1/models/<model-name>:predict`) to send a test request. The **model name** can be retrieved from the `/v1/models` endpoint on your serving URL. You will need the full predict URL in [Step 7](../07_build_app/).

---

## Navigation

| | |
|---|---|
| **⬅ Previous** | [Step 5 — Model Registry](../05_model_registry/) |
| **Next ➡**     | [Step 7 — Build App →](../07_build_app/) |
| **🏠 Overview** | [Move-It overview](../README.md) |
