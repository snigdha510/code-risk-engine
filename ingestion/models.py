from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class FunctionMetadata:
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str]
    source_code: str
    calls: List[str] = field(default_factory=list)