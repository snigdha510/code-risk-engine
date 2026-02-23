from ingestion.repo_scanner import scan_repository
from graph.dependency_builder import build_dependency_graph, compute_dependency_depth
from decision.risk_engine import compute_risk_score
import networkx as nx
from retrieval.vector_store import VectorStore
from decision.llm_agent import DecisionAgent
from decision.llm_client import call_llm

agent = DecisionAgent(call_llm)


def get_functions_in_file(functions, file_path):
    return [
        fn for fn in functions
        if fn.file_path.endswith(file_path)
    ]


def find_function_by_line(functions, file_path, line_number):
    for fn in functions:
        if (
            fn.file_path == file_path
            and fn.start_line <= line_number <= fn.end_line
        ):
            return fn
    return None


if __name__ == "__main__":
    repo_path = "repos/sample_app"

    # Step 1: Extract functions
    functions = scan_repository(repo_path)
    print(f"Extracted {len(functions)} functions")

    if not functions:
        print("No functions extracted. Check repo path.")
        exit()

    # Step 2: Build graph
    graph = build_dependency_graph(functions)
    print(f"Graph has {graph.number_of_nodes()} nodes")
    print(f"Graph has {graph.number_of_edges()} edges")

    centrality = nx.betweenness_centrality(graph)

    # Step 3: Build vector store
    vector_store = VectorStore()
    vector_store.add_functions(functions)
    print("Vector index built.")

    # -------------------------------
    # 🔥 Simulate single-line change
    # -------------------------------

    modified_file = "repos/sample_app/auth.py"
    modified_line = 10  # pick a line inside authenticate()

    fn = find_function_by_line(functions, modified_file, modified_line)

    if fn:
        node_id = f"{fn.file_path}::{fn.name}"

        impact_size = len(nx.descendants(graph, node_id))
        depth = compute_dependency_depth(graph, node_id)
        reverse_impact = len(nx.ancestors(graph, node_id))
        centrality_score = centrality.get(node_id, 0)

        risk_score = compute_risk_score(
            impact_size,
            depth,
            centrality_score,
            reverse_impact
        )

        similar_functions = vector_store.search_similar(fn.source_code, top_k=3)

        print("\nSimulated single-line modification:")
        print(f"Function: {fn.name}")
        print(f"Impact size: {impact_size}")
        print(f"Depth: {depth}")
        print(f"Reverse dependency: {reverse_impact}")
        print(f"Risk: {risk_score}")

        print("\nSemantically similar functions:")
        for sim_fn in similar_functions:
            print(f"- {sim_fn.name} ({sim_fn.file_path})")

        # 🔥 LLM decision layer
        decision = agent.evaluate(
            function_name=fn.name,
            source_code=fn.source_code,
            impact_size=impact_size,
            depth=depth,
            reverse_dependency=reverse_impact,
            similar_functions=similar_functions
        )

        print("\nFinal AI Decision:")
        print(decision)