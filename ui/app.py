import streamlit as st
import requests

st.set_page_config(
    page_title="AI Code Risk Analyzer",
    page_icon="🧠",
    layout="wide"
)

API_BASE = "http://localhost:8000"

if "repo_path" not in st.session_state:
    st.session_state["repo_path"] = None

st.title("🧠 AI Code Risk Analyzer")
st.markdown("Analyze structural and semantic risk of functions inside any repository.")

with st.sidebar:
    st.header("📂 Repository Input")

    mode = st.radio("Select Input Type", ["Upload ZIP", "GitHub URL"])

    if mode == "Upload ZIP":
        uploaded_file = st.file_uploader("Upload repository ZIP")

        if uploaded_file and st.button("Upload Repository"):
            files = {"file": uploaded_file}

            response = requests.post(
                f"{API_BASE}/upload-repo",
                files=files
            )

            if response.status_code == 200:
                st.session_state["repo_path"] = response.json()["repo_path"]
                st.success("Repository uploaded successfully!")

    elif mode == "GitHub URL":
        repo_url = st.text_input("Enter GitHub Repository URL")

        if st.button("Clone Repository"):
            response = requests.post(
                f"{API_BASE}/clone-github",
                json={"repo_url": repo_url}
            )

            if response.status_code == 200:
                st.session_state["repo_path"] = response.json()["repo_path"]
                st.success("Repository cloned successfully!")

if st.session_state["repo_path"]:
    st.success("Repository ready. Use the pages in the sidebar to explore analysis.")