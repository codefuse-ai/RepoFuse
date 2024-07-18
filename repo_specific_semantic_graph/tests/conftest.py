"""This module contains common fixtures for the tests that can be shared across multiple test modules."""

from pathlib import Path

import pytest


@pytest.fixture
def repo_suite_path():
    return Path(__file__).parent / "code_example"


@pytest.fixture
def python_repo_suite_path(repo_suite_path):
    return repo_suite_path / "python"


@pytest.fixture
def java_repo_suite_path(repo_suite_path):
    return repo_suite_path / "java"


@pytest.fixture
def c_sharp_repo_suite_path(repo_suite_path):
    return repo_suite_path / "c_sharp"


@pytest.fixture
def javascript_repo_suite_path(repo_suite_path):
    return repo_suite_path / "javascript"


@pytest.fixture
def typescript_repo_suite_path(repo_suite_path):
    return repo_suite_path / "typescript"
