from pathlib import Path

import chardet

from dependency_graph.models import PathLike


def detect_file_encoding(file_path: Path) -> str:
    """Function to detect encoding"""
    # Read the file as binary data
    raw_data = file_path.read_bytes()
    # Detect encoding
    detected = chardet.detect(raw_data)
    encoding = detected["encoding"]
    return encoding


def read_file_to_string(file_path: PathLike) -> str:
    """Function to detect encoding and read file to string"""
    if isinstance(file_path, str):
        file_path = Path(file_path)

    encoding = detect_file_encoding(file_path)

    # Read the file with the detected encoding
    content = file_path.read_text(encoding=encoding)

    return content
