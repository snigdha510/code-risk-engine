from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os
import subprocess
import uuid
import networkx as nx

from ingestion.repo_scanner import scan_repository
from graph.dependency_builder import build_dependency_graph, compute_dependency_depth
from decision.risk_engine import compute_risk_score
from service.analyzer import analyze_specific_function

app = FastAPI()

BASE_DIR = "uploaded_repos"
os.makedirs(BASE_DIR, exist_ok=True)

# =========================
# Request Models
# =========================

class GitHubRequest(BaseModel):
    repo_url: str


class RepoRequest(BaseModel):
    repo_path: str


class FunctionRequest(BaseModel):
    repo_path: str
    file: str
    function: str


class SourceRequest(BaseModel):
    repo_path: str
    file: str
    function: str


# =========================
# Upload ZIP
# =========================

@app.post("/upload-repo")
async def upload_repo(file: UploadFile = File(...)):
    temp_id = str(uuid.uuid4())
    repo_path = os.path.join(BASE_DIR, temp_id)

    os.makedirs(repo_path, exist_ok=True)

    zip_path = os.path.join(repo_path, file.filename)

    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    shutil.unpack_archive(zip_path, repo_path)

    return {"repo_path": repo_path}


# =========================
# Clone GitHub
# =========================

@app.post("/clone-github")
def clone_github(request: GitHubRequest):
    temp_id = str(uuid.uuid4())
    repo_path = os.path.join(BASE_DIR, temp_id)

    subprocess.run(["git", "clone", request.repo_url, repo_path])

    return {"repo_path": repo_path}


# =========================
# Scan Functions
# =========================

@app.post("/scan-functions")
def scan_functions(request: RepoRequest):
    functions = scan_repository(request.repo_path)

    if not functions:
        return {"error": "No functions found"}

    return {
        "functions": [
            {"file": fn.file_path, "name": fn.name}
            for fn in functions
        ]
    }


# =========================
# Analyze Function
# =========================

@app.post("/analyze-function")
def analyze_function(request: FunctionRequest):
    return analyze_specific_function(
        request.repo_path,
        request.file,
        request.function
    )


# =========================
# Repo Risk Ranking
# =========================

@app.post("/repo-risk-ranking")
def repo_risk_ranking(request: RepoRequest):

    functions = scan_repository(request.repo_path)
    if not functions:
        return []

    graph = build_dependency_graph(functions)
    centrality = nx.degree_centrality(graph)

    results = []

    for fn in functions:
        node_id = f"{fn.file_path}::{fn.name}"

        impact_size = len(nx.descendants(graph, node_id))
        depth = compute_dependency_depth(graph, node_id)
        reverse_impact = len(nx.ancestors(graph, node_id))
        centrality_score = centrality.get(node_id, 0)

        risk_score = compute_risk_score(
            impact_size,
            depth,
            centrality_score,
            reverse_impact,
        )

        results.append({
            "file": fn.file_path,
            "function": fn.name,
            "risk_score": round(risk_score, 4),
        })

    ranked = sorted(results, key=lambda x: x["risk_score"], reverse=True)

    return ranked[:50]


# =========================
# Dependency Graph
# =========================

@app.post("/dependency-graph")
def dependency_graph(request: RepoRequest):

    functions = scan_repository(request.repo_path)
    if not functions:
        return {"nodes": [], "edges": []}

    graph = build_dependency_graph(functions)

    return {
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges())
    }


# =========================
# Source Viewer
# =========================

@app.post("/get-function-source")
def get_function_source(request: SourceRequest):

    functions = scan_repository(request.repo_path)

    for fn in functions:
        if (
            fn.file_path.endswith(request.file)
            and fn.name == request.function
        ):
            return {"source": fn.source_code}

    return {"source": "Function not found"}