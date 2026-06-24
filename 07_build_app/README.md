# Step 7 — Build App (Dashboard)

**Move-It** › **Streamlit Dashboard** · `07_build_app/`

|| |
|---|---|
| **⬅ Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **🏁 Next**     | — (journey complete) |

The final step: Build and deploy a **Streamlit Dashboard** to monitor real-time sensor data and visualize irrigation decisions.

---

## What’s In This Step?

- **Streamlit UI:** Displays real-time telemetry (Temp, Humidity) and predictions.
- **Integrated Simulator:** A built-in button to mimic sensor data via HTTP POST.
- **Kafka Consumer:** Listens to the live stream and updates the dashboard automatically.

---

## Quick Start

1. **Install Dependencies:**
   ```bash
   cd 07_build_app
   pip install -r requirements.txt
   ```
2. **Run the Dashboard:**
   ```bash
   # Ensure your KAFKA_BROKER and INGEST_API_URL are set
   streamlit run app.py
   ```
3. **Start the Simulation:**
   Click the **▶️ Start Simulation** button in the sidebar of the Streamlit app.

---

## Navigation

|| |
|---|---|
| **⬅ Previous** | [Step 6 — Deploy Model](../06_deploy_model/) |
| **🏁 Next** | — (journey complete) |
| **🏠 Overview** | [Move-It overview](../README.md) |
