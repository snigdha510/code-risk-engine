import streamlit as st
import requests

API_BASE = "https://code-risk-backend.onrender.com"

st.title("📄 Source Code Viewer")

if "repo_path" not in st.session_state or not st.session_state["repo_path"]:
    st.warning("Upload or clone a repository first.")
    st.stop()

scan_response = requests.post(
    f"{API_BASE}/scan-functions",
    json={"repo_path": st.session_state["repo_path"]}
)

functions = scan_response.json()["functions"]

options = [
    f"{f['file']} :: {f['name']}"
    for f in functions
]

selected = st.selectbox("Select Function", options)

if st.button("View Source"):
    file_name, function_name = selected.split(" :: ")

    response = requests.post(
        f"{API_BASE}/get-function-source",
        json={
            "repo_path": st.session_state["repo_path"],
            "file": file_name,
            "function": function_name
        }
    )

    if response.status_code == 200:
        source = response.json()["source"]
        st.code(source, language="python")