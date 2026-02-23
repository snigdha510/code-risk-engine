import networkx as nx
from typing import List
from ingestion.models import FunctionMetadata


def build_dependency_graph(functions: List[FunctionMetadata]):
    graph = nx.DiGraph()

    # Create unique identifier
    def node_id(fn: FunctionMetadata):
        return f"{fn.file_path}::{fn.name}"

    # Add nodes
    for fn in functions:
        graph.add_node(node_id(fn), file=fn.file_path, name=fn.name)

    # Map function names to full IDs
    name_to_ids = {}
    for fn in functions:
        name_to_ids.setdefault(fn.name, []).append(node_id(fn))

    # Add edges
    for fn in functions:
        caller_id = node_id(fn)

        for call in fn.calls:

            # 🔥 Handle self.method()
            if call.startswith("SELF::"):
                method_name = call.replace("SELF::", "")
                class_name = fn.name.split(".")[0]

                qualified = f"{class_name}.{method_name}"

                if qualified in name_to_ids:
                    for callee_id in name_to_ids[qualified]:
                        graph.add_edge(caller_id, callee_id)

            # Regular function call
            elif call in name_to_ids:
                for callee_id in name_to_ids[call]:
                    graph.add_edge(caller_id, callee_id)

    return graph

def compute_dependency_depth(graph, node_id):
    max_depth = 0
    for target in nx.descendants(graph, node_id):
        try:
            depth = nx.shortest_path_length(graph, node_id, target)
            max_depth = max(max_depth, depth)
        except nx.NetworkXNoPath:
            continue
    return max_depth