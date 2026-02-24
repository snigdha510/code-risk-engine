import os
import networkx as nx

from ingestion.repo_scanner import scan_repository
from graph.dependency_builder import (
    build_dependency_graph,
    compute_dependency_depth,
)
from decision.risk_engine import compute_risk_score
# from retrieval.vector_store import VectorStore
from decision.llm_agent import DecisionAgent
from decision.llm_client import call_llm


# ----------------------------
# Helper: find function by line
# ----------------------------
def find_function_by_line(functions, file_path, line_number):
    for fn in functions:
        if (
            fn.file_path.endswith(file_path)
            and fn.start_line <= line_number <= fn.end_line
        ):
            return fn
    return None


# ----------------------------
# Core Analyzer Function
# ----------------------------
def analyze_repository(repo_path: str, modified_file: str, modified_line: int):
    """
    Main entry point for risk analysis.

    Args:
        repo_path: path to cloned repository
        modified_file: relative file path inside repo
        modified_line: line number that changed

    Returns:
        dict with full structured analysis
    """

    if not os.path.exists(repo_path):
        return {"error": "Repository path does not exist"}

    # ----------------------------
    # 1️⃣ Extract functions
    # ----------------------------
    functions = scan_repository(repo_path)

    if not functions:
        return {"error": "No functions detected in repository"}

    # ----------------------------
    # 2️⃣ Build dependency graph
    # ----------------------------
    graph = build_dependency_graph(functions)
    centrality = nx.betweenness_centrality(graph)

    # ----------------------------
    # 3️⃣ Locate modified function
    # ----------------------------
    fn = find_function_by_line(functions, modified_file, modified_line)

    if not fn:
        return {"error": "No function found at specified file/line"}

    node_id = f"{fn.file_path}::{fn.name}"
    print([fn.file_path for fn in functions])

    # ----------------------------
    # 4️⃣ Structural Risk Metrics
    # ----------------------------
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

    # ----------------------------
    # 5️⃣ Semantic Retrieval
    # ----------------------------
    # vector_store = VectorStore()
    # vector_store.add_functions(functions)

    # similar_functions = vector_store.search_similar(
    #     fn.source_code, top_k=3
    # )

    similar_functions = []

    # ----------------------------
    # 6️⃣ LLM Decision Agent
    # ----------------------------
    agent = DecisionAgent(call_llm)

    decision = agent.evaluate(
        function_name=fn.name,
        source_code=fn.source_code,
        impact_size=impact_size,
        depth=depth,
        reverse_dependency=reverse_impact,
        similar_functions=similar_functions,
    )

    # ----------------------------
    # 7️⃣ Final Structured Output
    # ----------------------------
    result = {
        "modified_function": fn.name,
        "file": modified_file,
        "line": modified_line,
        "structural_metrics": {
            "impact_size": impact_size,
            "dependency_depth": depth,
            "reverse_dependency": reverse_impact,
            "centrality": round(centrality_score, 4),
            "risk_score": risk_score,
        },
        "semantic_neighbors": [
            {
                "name": sim_fn.name,
                "file": sim_fn.file_path,
            }
            for sim_fn in similar_functions
        ],
        "llm_decision": decision,
    }

    return result

def analyze_specific_function(repo_path: str, target_file: str, target_function: str):
    if not os.path.exists(repo_path):
        return {"error": "Repository path does not exist"}

    # 1️⃣ Extract functions
    functions = scan_repository(repo_path)

    if not functions:
        return {"error": "No functions detected in repository"}

    # 2️⃣ Build dependency graph
    graph = build_dependency_graph(functions)
    centrality = nx.betweenness_centrality(graph)

    # 3️⃣ Locate target function
    target_fn = None
    for fn in functions:
        if (
            fn.file_path.endswith(target_file)
            and fn.name == target_function
        ):
            target_fn = fn
            break

    if not target_fn:
        return {"error": "Function not found"}

    node_id = f"{target_fn.file_path}::{target_fn.name}"

    # 4️⃣ Structural Metrics
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

    # 5️⃣ Semantic Retrieval
    # vector_store = VectorStore()
    # vector_store.add_functions(functions)

    # similar_functions = vector_store.search_similar(
    #     target_fn.source_code, top_k=3
    # )

    similar_functions = []

    # 6️⃣ LLM Decision
    agent = DecisionAgent(call_llm)

    decision = agent.evaluate(
        function_name=target_fn.name,
        source_code=target_fn.source_code,
        impact_size=impact_size,
        depth=depth,
        reverse_dependency=reverse_impact,
        similar_functions=similar_functions,
    )

    # 7️⃣ Return structured output
    return {
        "modified_function": target_fn.name,
        "file": target_file,
        "structural_metrics": {
            "impact_size": impact_size,
            "dependency_depth": depth,
            "reverse_dependency": reverse_impact,
            "centrality": round(centrality_score, 4),
            "risk_score": risk_score,
        },
        "semantic_neighbors": [
            {
                "name": sim_fn.name,
                "file": sim_fn.file_path,
            }
            for sim_fn in similar_functions
        ],
        "llm_decision": decision,
    }