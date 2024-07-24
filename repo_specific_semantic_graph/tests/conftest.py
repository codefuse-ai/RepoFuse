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


@pytest.fixture
def kotlin_repo_suite_path(repo_suite_path):
    return repo_suite_path / "kotlin"


@pytest.fixture
def php_repo_suite_path(repo_suite_path):
    return repo_suite_path / "php"


@pytest.fixture
def ruby_repo_suite_path(repo_suite_path):
    return repo_suite_path / "ruby"


@pytest.fixture
def c_repo_suite_path(repo_suite_path):
    return repo_suite_path / "c"


@pytest.fixture
def cpp_repo_suite_path(repo_suite_path):
    return repo_suite_path / "cpp"


@pytest.fixture
def go_repo_suite_path(repo_suite_path):
    return repo_suite_path / "go"


@pytest.fixture
def swift_repo_suite_path(repo_suite_path):
    return repo_suite_path / "swift"


@pytest.fixture
def rust_repo_suite_path(repo_suite_path):
    return repo_suite_path / "rust"
