import sys

from mypy.modulefinder import BuildSource
from mypy.stubgen import (
    ASTStubGenerator,
    StubSource,
    generate_asts_for_modules,
    mypy_options,
    Options,
)


def generate_python_stub(code: str):
    options = Options(
        pyversion=sys.version_info[:2],
        no_import=True,
        inspect=False,
        doc_dir="",
        search_path=[],
        interpreter=sys.executable,
        ignore_errors=True,
        parse_only=True,
        include_private=False,
        output_dir="/tmp/out",
        modules=[],
        packages=[],
        files=["/tmp/mock.py"],
        verbose=False,
        quiet=True,
        export_less=True,
        include_docstrings=True,
    )
    mypy_opts = mypy_options(options)

    stub_source = StubSource("test", None)
    stub_source.source = BuildSource(None, None, text=code)
    generate_asts_for_modules([stub_source], False, mypy_opts, False)

    gen = ASTStubGenerator(
        stub_source.runtime_all,
        include_private=False,
        analyzed=True,
        export_less=False,
        include_docstrings=True,
    )
    stub_source.ast.accept(gen)
    output = gen.output()
    return output
