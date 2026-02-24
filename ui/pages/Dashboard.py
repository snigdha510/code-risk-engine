import streamlit as st
import requests

API_BASE = "https://code-risk-backend.onrender.com"

st.title("📊 Function Risk Dashboard")

if "repo_path" not in st.session_state or not st.session_state["repo_path"]:
    st.warning("Upload or clone a repository first.")
    st.stop()

scan_response = requests.post(
    f"{API_BASE}/scan-functions",
    json={"repo_path": st.session_state["repo_path"]}
)

if scan_response.status_code != 200:
    st.error("Failed to scan functions.")
    st.stop()

functions = scan_response.json()["functions"]

options = [
    f"{f['file']} :: {f['name']}"
    for f in functions
]

selected = st.selectbox("Select Function", options)

if st.button("Analyze Function"):
    file_name, function_name = selected.split(" :: ")

    result = requests.post(
        f"{API_BASE}/analyze-function",
        json={
            "repo_path": st.session_state["repo_path"],
            "file": file_name,
            "function": function_name
        }
    )

    if result.status_code == 200:
        data = result.json()

        risk = data["llm_decision"]["risk_level"]
        confidence = data["llm_decision"]["confidence"]
        metrics = data["structural_metrics"]

        col1, col2 = st.columns([2, 1])

        with col1:
            if risk == "HIGH":
                st.error(f"🚨 Risk Level: {risk}")
            elif risk == "MEDIUM":
                st.warning(f"⚠️ Risk Level: {risk}")
            else:
                st.success(f"✅ Risk Level: {risk}")

            st.caption(f"Confidence: {confidence*100:.0f}%")

        with col2:
            st.metric("Risk Score", round(metrics["risk_score"], 3))
            st.progress(min(metrics["risk_score"], 1.0))

        st.markdown("### 📊 Structural Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Impact Size", metrics["impact_size"])
        c2.metric("Dependency Depth", metrics["dependency_depth"])
        c3.metric("Reverse Dependencies", metrics["reverse_dependency"])

        with st.expander("🤖 AI Reasoning"):
            st.write(data["llm_decision"]["reasoning"])