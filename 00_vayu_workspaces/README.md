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

For the full create wizard (Start → Infrastructure → Configure Compute and Storage → Observability → Review), see the [Workspace documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/workspace/).

---

## 🚀 Getting Started

1. **Create a Vayu AI Studio Workspace**

   - Log in to [Vayu AI Studio](https://ipcloud.tatacommunications.com/aistudio/#/build/workspace-list).
   - Click **Create Workspace** and follow the prompts. See the [Workspace documentation](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/workspace/) for step-by-step wizard details.
   - Make sure **Enable Docker in the Workspace** is turned on before you finish creating the workspace.

2. **Import This Repository**

   - Clone or upload the `move-it` GitHub repository into your new workspace.

   ```bash
   git clone https://github.com/your-org/move-it.git
   ```

   Or, upload it manually via the UI.

3. **Install Python Dependencies**

   Inside your workspace terminal:

   ```bash
   cd move-it
   pip install -r requirements.txt
   ```

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
