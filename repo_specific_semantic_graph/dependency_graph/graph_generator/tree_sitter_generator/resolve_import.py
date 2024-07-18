from pathlib import Path
from textwrap import dedent

from tree_sitter import Language as TS_Language, Parser, Tree, Node as TS_Node

from dependency_graph.graph_generator.tree_sitter_generator.load_lib import (
    get_builtin_lib_path,
)
from dependency_graph.models import PathLike
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.read_file import read_file_to_string

FIND_IMPORT_QUERY = {
    Language.Java: dedent(
        """
        (import_declaration
        [
          (identifier) @import_name
          (scoped_identifier) @import_name
        ])
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

    def _query_and_captures(self, code: str, query: str):
        tree: Tree = self.parser.parse(code.encode())
        query = self.ts_language.query(query)
        captures = query.captures(tree.root_node)
        return [node for node, _ in captures]

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
            case Language.Java:
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
            case Language.TypeScript | Language.JavaScript:
                return file_path.stem


class ImportResolver:
    def __init__(self, language: Language):
        self.language = language

    def resolve_import(
        self,
        importee_class_name: str,
        module_map: dict[str, list[Path]],
        importer_file_path: Path,
    ) -> list[Path] | None:
        match self.language:
            case Language.Java | Language.CSharp:
                return module_map.get(importee_class_name, None)
            case Language.TypeScript | Language.JavaScript:
                return self.resolve_ts_js_import(
                    importee_class_name, module_map, importer_file_path
                )
            case _:
                raise NotImplementedError(f"Language {self.language} is not supported")

    def resolve_ts_js_import(
        self,
        importee_class_name: str,
        module_map: dict[str, list[Path]],
        importer_file_path: PathLike,
    ) -> list[Path] | None:
        def _search_file(search_path: Path, module_name: str) -> list[Path]:
            result_path = []
            for ext in extension_list:
                if (search_path / f"{module_name}{ext}").exists():
                    result_path.append(search_path / f"{module_name}{ext}")
                elif (search_path / f"{module_name}").is_dir():
                    """
                    In case the module is a directory, we should search for the `module_dir/index.{js|ts}` file
                    """
                    for ext in extension_list:
                        if (search_path / f"{module_name}" / f"index{ext}").exists():
                            result_path.append(
                                search_path / f"{module_name}" / f"index{ext}"
                            )
                    break
            return result_path

        extension_list = (
            Repository.code_file_extensions[Language.TypeScript]
            + Repository.code_file_extensions[Language.JavaScript]
        )

        # Find the module path
        # e.g. './Descriptor' -> './Descriptor.ts'; '../Descriptor' -> '../Descriptor.ts'
        if "." in importee_class_name or ".." in importee_class_name:

            result_path = None
            # If there is a suffix in the name
            if suffix := Path(importee_class_name).suffix:
                # In case of '../package.json', we should filter it out
                path = importer_file_path.parent / importee_class_name
                if suffix in extension_list and path.exists():
                    result_path = [path]
            else:
                result_path = _search_file(
                    importer_file_path.parent, importee_class_name
                )
            return result_path
        else:
            return module_map.get(importee_class_name, None)
