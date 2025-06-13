import os
from pathlib import Path
from typing import Dict, List, Union

IGNORE_PATTERNS = ['.git', '__pycache__', '.pytest_cache', '.venv', 'venv']
READABLE_EXTENSIONS = ['py', 'js', 'ts', 'tsx', 'java', 'go', 'html', 'css', 'json', 'yml', 'yaml', 'Dockerfile']

def read_file_content(file_path: Path, max_chars: int = 3000) -> str:
    try:
        if not file_path.exists():
            return f"[Missing file: {file_path}]"
        if not file_path.is_file():
            return f"[Skipping non-file path: {file_path}]"
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()[:max_chars]
    except Exception as e:
        return f"[Error reading file: {file_path}: {e}]"

def read_directory_structure(directory_path: Union[str, Path], ignore_patterns: List[str] = None) -> Dict:
    if ignore_patterns is None:
        ignore_patterns = IGNORE_PATTERNS

    directory_path = Path(directory_path)
    if not directory_path.exists():
        return {"error": f"Directory {directory_path} does not exist"}

    result = {
        "path": str(directory_path.resolve()),
        "name": directory_path.name,
        "type": "directory",
        "children": []
    }

    try:
        for item in directory_path.iterdir():
            if any(pattern in str(item) for pattern in ignore_patterns):
                continue
            if item.is_file():
                file_info = {
                    "name": item.name,
                    "path": str(item.resolve()),
                    "extension": item.suffix[1:] if item.suffix else "",
                    "type": "file"
                }
                result["children"].append(file_info)
            elif item.is_dir():
                result["children"].append(read_directory_structure(item, ignore_patterns))
    except PermissionError:
        return {"error": f"Permission denied for {directory_path}"}

    return result

def generate_llm_chunks_inline(directory_path: Union[str, Path]) -> List[str]:
    directory_path = Path(directory_path)
    chunks = []

    def traverse(node):
        if node["type"] == "file":
            file_path = Path(node.get("path", ""))
            ext = node.get("extension", "")
            # Check if file is readable either by extension or by name
            if ext in READABLE_EXTENSIONS or file_path.name in READABLE_EXTENSIONS:
                content = read_file_content(file_path)
                chunk = f"# File: {file_path}\n{content}\n\n=== END OF FILE ===\n\n"
                chunks.append(chunk)
        elif node["type"] == "directory":
            for child in node.get("children", []):
                traverse(child)

    structure = read_directory_structure(directory_path)
    traverse(structure)
    return chunks
