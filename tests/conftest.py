"""This module contains common fixtures for the tests that can be shared across multiple test modules."""
from pathlib import Path

import pytest


@pytest.fixture
def repo_suite_path():
    return Path(__file__).parent / "code_example"


@pytest.fixture
def python_repo_suite_path(repo_suite_path):
    return repo_suite_path / "python"
