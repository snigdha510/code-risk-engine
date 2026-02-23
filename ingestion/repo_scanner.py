import os
from typing import List
from ingestion.parser import extract_functions_from_file
from ingestion.models import FunctionMetadata
from tqdm import tqdm


def scan_repository(repo_path: str) -> List[FunctionMetadata]:
    all_functions = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                functions = extract_functions_from_file(full_path)
                all_functions.extend(functions)

    return all_functions
