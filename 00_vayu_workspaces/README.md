# Step 0: Set up Your Vayu AI Studio Workspace

Welcome to **Move-It**!  
This step will help you set up the Vayu AI Studio Workspace required for your IoT data pipeline and machine learning training.

---

## 📝 Quick Navigation

|         |                                                |
|---------|------------------------------------------------|
| **⬅️ Previous** | [Move-It Overview](../README.md)              |
| **➡️ Next**     | [Step 1 — Vayu Object Storage](../01_dataset/)    |

---

## Workspace Overview

![Vayu AI Studio Workspace Overview](../assets/workspaces.png)

---

## Open Workspace

Go to [Vayu AI Studio Workspace](https://ipcloud.tatacommunications.com/aistudio/#/build/workspace-list).

For the full create wizard (Start → Infrastructure → Configure Compute and Storage → Observability → Review), see the [Creating Workspace guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/workspace/#creating-workspace).

---

## 🚀 Getting Started

1. **Create a Vayu AI Studio Workspace**

   > ## ⏭️ **SKIP THIS STEP** if a Vayu AI Studio workspace has already been provided to you — continue with step 2 below.

   - Log in to [Vayu AI Studio](https://ipcloud.tatacommunications.com/aistudio/#/build/workspace-list).
   - Click **Create Workspace** and follow the prompts. See the [Creating Workspace guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/workspace/#creating-workspace) for step-by-step wizard details.
   - **Object storage host alias:** During workspace creation, add a **host alias** for object storage using the **IP** and **endpoint** from your provided SOP document. Enter the endpoint as the hostname **only** — do not include `http://` or `https://`.
   - Make sure **Enable Docker in the Workspace** is turned on before you finish creating the workspace.

2. **Import This Repository**

   Clone the `move-it` repository into your new workspace:

   ```bash
   git clone https://ailab.cloudservices.tatacommunications.com/code/vayu-hackathon/move-it.git
   ```

   Or, upload it manually via the UI.

3. **Install Python Dependencies**

   Inside your workspace terminal:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   cd move-it
   pip install -r requirements.txt
   ```

4. **Select the notebook kernel**

   When you open any `.ipynb` in this project, use the virtual environment above:

   1. Open **Select Kernel** and choose **Python Environments**.

      ![Select Kernel — Python Environments](../assets/kernel_select.png)

   2. Under **Select a Python Environment**, pick the **Recommended** environment (it should point to the `.venv` you created).

      ![Select a Python Environment](../assets/Select_kernerl_env.png)

   3. **Validate the path:** Confirm the selected interpreter path ends with `<your-env-name>/bin/python` (for example, `.venv/bin/python` if you created `.venv` in step 3).

---

## 🔗 Resources

| Resource               | Link                                                                                           |
|------------------------|------------------------------------------------------------------------------------------------|
| Vayu AI Studio         | [Workspace Dashboard](https://ipcloud.tatacommunications.com/aistudio/#/build/workspace-list)        |
| Documentation          | [Workspace documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/workspace/) |

---

## 📂 Project Navigation

|         |                                                |
|---------|------------------------------------------------|
| **⬅️ Previous** | [Move-It Overview](../README.md)              |
| **➡️ Next**     | [Step 1 — Vayu Object Storage](../01_dataset/)    |
| **Overview**    | [Move-It Overview](../README.md)              |
