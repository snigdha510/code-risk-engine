import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import os

API_BASE = "https://code-risk-backend.onrender.com"


st.title("🕸 Dependency Graph")

if "repo_path" not in st.session_state or not st.session_state["repo_path"]:
    st.warning("Upload or clone a repository first.")
    st.stop()

response = requests.post(
    f"{API_BASE}/dependency-graph",
    json={"repo_path": st.session_state["repo_path"]}
)

if response.status_code != 200:
    st.error("Failed to generate graph.")
    st.write(response.text)
    st.stop()

graph_data = response.json()

nodes = graph_data["nodes"]
edges = graph_data["edges"]

if not nodes:
    st.warning("No dependency data available.")
    st.stop()

# ----------------------------
# Create Clean PyVis Graph
# ----------------------------

net = Network(
    height="750px",
    width="100%",
    bgcolor="#0E1117",
    font_color="white",
    directed=True
)

net.barnes_hut(
    gravity=-20000,
    central_gravity=0.3,
    spring_length=150,
    spring_strength=0.05,
    damping=0.09
)

# ----------------------------
# Add Nodes (Clean Labels)
# ----------------------------

for node in nodes:
    short_name = node.split("::")[-1]  # Only function name
    file_name = os.path.basename(node.split("::")[0])

    net.add_node(
        node,
        label=short_name,
        title=f"{file_name}<br>{node}",  # hover tooltip
        size=15
    )

# ----------------------------
# Add Edges
# ----------------------------

for edge in edges:
    net.add_edge(edge[0], edge[1])

# ----------------------------
# Save and Render
# ----------------------------

net.save_graph("graph.html")

with open("graph.html", "r", encoding="utf-8") as f:
    components.html(f.read(), height=750)