from pathlib import Path
from textwrap import dedent

from tree_sitter import Language, Parser, Tree, Node

from dependency_graph.graph_generator.tree_sitter_generator import get_builtin_lib_path

TS_LIB_PATH = Path(__file__).parent.parent / "lib"

SPECIAL_CHAR = b" "


def generate_java_stub(code: str, include_comments: bool = True) -> str:
    lib_path = get_builtin_lib_path(TS_LIB_PATH)

    # Initialize the Tree-sitter language
    language = Language(str(lib_path.absolute()), "java")
    parser = Parser()
    parser.set_language(language)

    code_bytes = code.encode()
    tree: Tree = parser.parse(code_bytes)

    code_has_changed = False
    code_bytes_arr = bytearray(code_bytes)

    # Remove import declaration
    query = language.query(
        dedent(
            """
            (import_declaration) @import
            """
        )
    )
    captures = query.captures(tree.root_node)
    for node, _ in captures:
        code_has_changed = True
        code_bytes_arr[node.start_byte : node.end_byte] = SPECIAL_CHAR * (
            node.end_byte - node.start_byte
        )

    # Remove method body
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

    for node, _ in captures:
        body: Node = node.child_by_field_name("body")
        if body:
            code_has_changed = True
            code_bytes_arr[body.start_byte : body.end_byte] = SPECIAL_CHAR * (
                body.end_byte - body.start_byte
            )

    # Remove comment
    if not include_comments:
        query = language.query(
            dedent(
                """
                [
                  (line_comment) @comment
                  (block_comment) @comment
                ]
                """
            )
        )
        captures = query.captures(tree.root_node)
        for node, _ in captures:
            code_has_changed = True
            code_bytes_arr[node.start_byte : node.end_byte] = SPECIAL_CHAR * (
                node.end_byte - node.start_byte
            )

    if code_has_changed:
        # rstrip the trailing whitespaces
        code = "\n".join([c.rstrip() for c in code_bytes_arr.decode().splitlines()])

    return code
