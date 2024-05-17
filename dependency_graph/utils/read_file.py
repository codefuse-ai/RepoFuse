from pathlib import Path

import chardet

from dependency_graph.models import PathLike


def detect_file_encoding(file_path: PathLike) -> str:
    """Function to detect encoding"""
    path = Path(file_path)
    # Read the file as binary data
    raw_data = path.read_bytes()
    # Detect encoding
    detected = chardet.detect(raw_data)
    encoding = detected["encoding"]
    return encoding


def read_file_to_string(file_path: PathLike) -> str:
    """Function to detect encoding and read file to string"""
    path = Path(file_path)

    encoding = detect_file_encoding(file_path)

    # Read the file with the detected encoding
    content = path.read_text(encoding=encoding)

    return content
