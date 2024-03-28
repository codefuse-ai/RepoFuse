from pathlib import Path
from textwrap import dedent

from tree_sitter import Language, Parser, Tree, Node

from dependency_graph.graph_generator.tree_sitter_generator import get_builtin_lib_path

TS_LIB_PATH = Path(__file__).parent.parent / "lib"

SPECIAL_CHAR = b" "


def generate_java_stub(code: str) -> str:
    lib_path = get_builtin_lib_path(TS_LIB_PATH)

    # Initialize the Tree-sitter language
    language = Language(str(lib_path.absolute()), "java")
    parser = Parser()
    parser.set_language(language)

    code_bytes = code.encode()
    tree: Tree = parser.parse(code_bytes)

    query = language.query(
        dedent(
            """
            [
              (constructor_declaration) @decl
              (method_declaration) @decl
            ]
            """
        )
    )
    captures = query.captures(tree.root_node)

    code_bytes_arr = bytearray(code_bytes)
    code_has_changed = False
    for node, _ in captures:
        body: Node = node.child_by_field_name("body")
        if body:
            code_has_changed = True
            code_bytes_arr[body.start_byte : body.end_byte] = SPECIAL_CHAR * (
                body.end_byte - body.start_byte
            )

    if code_has_changed:
        # rstrip the trailing whitespaces
        code = "\n".join([c.rstrip() for c in code_bytes_arr.decode().splitlines()])

    return code
