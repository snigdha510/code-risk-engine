import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.title("📈 Repository Risk Ranking")

if "repo_path" not in st.session_state or not st.session_state["repo_path"]:
    st.warning("Upload or clone a repository first.")
    st.stop()

response = requests.post(
    f"{API_BASE}/repo-risk-ranking",
    json={"repo_path": st.session_state["repo_path"]}
)

if response.status_code != 200:
    st.error("Failed to compute repository ranking.")
    st.stop()

data = response.json()

df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)