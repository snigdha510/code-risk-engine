import ast
from typing import List
from ingestion.models import FunctionMetadata


class FunctionExtractor(ast.NodeVisitor):
    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code.splitlines()
        self.file_path = file_path
        self.functions = []
        self.current_class = None
        self.class_instances = {}  # 🔥 NEW: track self.<var> → ClassName mapping

    def visit_ClassDef(self, node: ast.ClassDef):
        previous_class = self.current_class
        previous_instances = self.class_instances.copy()

        self.current_class = node.name
        self.class_instances = {}

        # 🔥 Scan __init__ to detect instance assignments
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                for subnode in ast.walk(stmt):
                    if isinstance(subnode, ast.Assign):
                        target = subnode.targets[0]

                        # Detect: self.db = Database()
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                            and isinstance(subnode.value, ast.Call)
                            and isinstance(subnode.value.func, ast.Name)
                        ):
                            instance_name = target.attr
                            class_name = subnode.value.func.id
                            self.class_instances[instance_name] = class_name

        self.generic_visit(node)

        self.current_class = previous_class
        self.class_instances = previous_instances

    def visit_FunctionDef(self, node: ast.FunctionDef):
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", node.lineno)

        source_segment = "\n".join(
            self.source_code[start_line - 1:end_line]
        )

        docstring = ast.get_docstring(node)

        # 🔥 Pass instance map into CallCollector
        call_collector = CallCollector(self.class_instances)
        call_collector.visit(node)

        # Fully qualified name
        if self.current_class:
            qualified_name = f"{self.current_class}.{node.name}"
        else:
            qualified_name = node.name

        function_data = FunctionMetadata(
            name=qualified_name,
            file_path=self.file_path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            source_code=source_segment,
            calls=call_collector.calls,
        )

        self.functions.append(function_data)
        self.generic_visit(node)


class CallCollector(ast.NodeVisitor):
    def __init__(self, class_instances):
        self.calls = []
        self.class_instances = class_instances

    def visit_Call(self, node):
        # Case 1: plain function call
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)

        # Case 2: attribute call
        elif isinstance(node.func, ast.Attribute):

            # Case: self.method()
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"
            ):
                self.calls.append(f"SELF::{node.func.attr}")

            # Case: self.db.method()
            elif (
                isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "self"
            ):
                instance_name = node.func.value.attr
                method_name = node.func.attr

                if instance_name in self.class_instances:
                    class_name = self.class_instances[instance_name]
                    self.calls.append(f"{class_name}.{method_name}")

        self.generic_visit(node)


# Must remain outside class
def extract_functions_from_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        extractor = FunctionExtractor(source, file_path)
        extractor.visit(tree)

        return extractor.functions

    except Exception:
        return []