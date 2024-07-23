from pathlib import Path
from textwrap import dedent

from tree_sitter import Parser, Language as TS_Language, Node as TS_Node, Tree

from dependency_graph.graph_generator.tree_sitter_generator.load_lib import (
    get_builtin_lib_path,
)
from dependency_graph.models.language import Language
from dependency_graph.utils.read_file import read_file_to_string

FIND_IMPORT_QUERY = {
    # Language.Python: dedent(
    #     """
    #     [
    #       (import_from_statement
    #         module_name: [
    #             (dotted_name) @import_name
    #             (relative_import) @import_name
    #         ]
    #       )
    #       (import_statement
    #         name: [
    #             (dotted_name) @import_name
    #             (aliased_import
    #                 name: (dotted_name) @import_name
    #             )
    #         ]
    #       )
    #     ]
    #     """
    # ),
    # For python, we need the whole import statement to analyze the import symbol
    Language.Python: dedent(
        """
        [
          (import_from_statement) @import_name
          (import_statement) @import_name
        ]
        """
    ),
    Language.Java: dedent(
        """
        (import_declaration
        [
          (identifier) @import_name
          (scoped_identifier) @import_name
        ])
        """
    ),
    Language.Kotlin: dedent(
        """
        (import_header (identifier) @import_name)
        """
    ),
    Language.CSharp: dedent(
        """
        (using_directive
        [
          (qualified_name) @package_name
          (identifier) @package_name
        ])
        """
    ),
    Language.TypeScript: dedent(
        """
        (import_statement (string (string_fragment) @import_name))
        """
    ),
    Language.JavaScript: dedent(
        """
        (import_statement (string (string_fragment) @import_name))
        """
    ),
    Language.PHP: dedent(
        """
        [
          (require_once_expression (string) @import_name)
          (require_expression (string) @import_name)
          (include_expression (string) @import_name)
        ]
        """
    ),
    Language.Ruby: dedent(
        """
        (call
            method: ((identifier) @require_name
                (#match? @require_name "require_relative|require")
            )
            arguments: (argument_list) @import_name
        )
        """
    ),
    Language.C: dedent(
        """
        (preproc_include path: 
            [
                (string_literal) @import_name
                (system_lib_string) @import_name
            ]
        )
        """
    ),
}
FIND_PACKAGE_QUERY = {
    Language.Java: dedent(
        """
        (package_declaration
        [
          (identifier) @package_name
          (scoped_identifier) @package_name
        ])
        """
    ),
    Language.Kotlin: dedent(
        """
        (package_header (identifier) @package_name)
        """
    ),
    Language.CSharp: dedent(
        """
        (namespace_declaration
        [
          (qualified_name) @namespace_name
          (identifier) @namespace_name
        ])
        """
    ),
}


class ImportFinder:
    def __init__(self, language: Language):
        lib_path = get_builtin_lib_path()
        self.language = language
        # Initialize the Tree-sitter language
        self.parser = Parser()
        self.ts_language = TS_Language(str(lib_path.absolute()), str(language))
        self.parser.set_language(self.ts_language)

    def _query_and_captures(
        self, code: str, query: str, capture_name="import_name"
    ) -> list[TS_Node]:
        """
        Query the Tree-sitter language and get the nodes that match the query
        :param code: The code to be parsed
        :param query: The query to be matched
        :param capture_name: The name of the capture group to be matched
        :return: The nodes that match the query
        """
        tree: Tree = self.parser.parse(code.encode())
        query = self.ts_language.query(query)
        captures = query.captures(tree.root_node)
        return [node for node, captured in captures if captured == capture_name]

    def find_imports(
        self,
        code: str,
    ) -> list[TS_Node]:
        return self._query_and_captures(code, FIND_IMPORT_QUERY[self.language])

    def find_module_name(self, file_path: Path) -> str:
        """
        Find the name of the module of the current file.
        This term is broad enough to encompass the different ways in which these languages organize and reference code units
        In Java, it is the name of the package.
        In C#, it is the name of the namespace.
        In JavaScript/TypeScript, it is the name of the file.
        """
        # Use read_file_to_string here to avoid non-UTF8 decoding issue
        code = read_file_to_string(file_path)
        match self.language:
            case Language.Java | Language.Kotlin:
                captures = self._query_and_captures(
                    code, FIND_PACKAGE_QUERY[self.language]
                )
                assert (
                    len(captures) == 1
                ), f"Expected 1 module in the file {file_path}, got {len(captures)}"
                node = captures[0]
                package_name = node.text.decode()
                module_name = f"{package_name}.{file_path.stem}"
                return module_name
            case Language.CSharp:
                captures = self._query_and_captures(
                    code, FIND_PACKAGE_QUERY[self.language]
                )
                assert (
                    len(captures) == 1
                ), f"Expected 1 module in the file {file_path}, got {len(captures)}"
                node = captures[0]
                namespace_name = node.text.decode()
                return namespace_name
            case (
                Language.TypeScript
                | Language.JavaScript
                | Language.Python
                | Language.Ruby
            ):
                return file_path.stem
            case Language.PHP | Language.C:
                return file_path.name
            case _:
                raise NotImplementedError(f"Language {self.language} is not supported")
