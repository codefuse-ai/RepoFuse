from pathlib import Path

from importlab.parsepy import ImportStatement
from importlab.resolve import ImportException
from tree_sitter import Node as TS_Node

from dependency_graph.graph_generator.tree_sitter_generator.python_resolver import (
    Resolver,
)
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


class ImportResolver:
    def __init__(self, repo: Repository):
        self.repo = repo

    def resolve_import(
        self,
        import_symbol_node: TS_Node,
        module_map: dict[str, list[Path]],
        importer_file_path: Path,
    ) -> list[Path] | None:
        match self.repo.language:
            case Language.Java | Language.Kotlin:
                import_symbol_name = import_symbol_node.text.decode()
                # Deal with star import: `import xxx.*`
                if b".*" in import_symbol_node.parent.text:
                    resolved_path_list = []
                    for module_name, path_list in module_map.items():
                        # Use rpartition to split the string at the rightmost '.'
                        package_name, _, _ = module_name.rpartition(".")
                        if package_name == import_symbol_name:
                            resolved_path_list.extend(path_list)
                    return resolved_path_list
                else:
                    return module_map.get(import_symbol_name, None)
            case Language.CSharp:
                import_symbol_name = import_symbol_node.text.decode()
                return module_map.get(import_symbol_name, None)
            case Language.TypeScript | Language.JavaScript:
                return self.resolve_ts_js_import(
                    import_symbol_node, module_map, importer_file_path
                )
            case Language.Python:
                return self.resolve_python_import(
                    import_symbol_node, importer_file_path
                )
            case Language.PHP:
                return self.resolve_php_import(import_symbol_node, importer_file_path)
            case Language.Ruby:
                return self.resolve_ruby_import(import_symbol_node, importer_file_path)
            case Language.C:
                return self.resolve_c_import(import_symbol_node, importer_file_path)
            case _:
                raise NotImplementedError(
                    f"Language {self.repo.language} is not supported"
                )

    def resolve_ts_js_import(
        self,
        import_symbol_node: TS_Node,
        module_map: dict[str, list[Path]],
        importer_file_path: Path,
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

        import_symbol_name = import_symbol_node.text.decode()
        extension_list = (
            Repository.code_file_extensions[Language.TypeScript]
            + Repository.code_file_extensions[Language.JavaScript]
        )

        # Find the module path
        # e.g. './Descriptor' -> './Descriptor.ts'; '../Descriptor' -> '../Descriptor.ts'
        if "." in import_symbol_name or ".." in import_symbol_name:

            result_path = None
            # If there is a suffix in the name
            if suffix := Path(import_symbol_name).suffix:
                # In case of '../package.json', we should filter it out
                path = importer_file_path.parent / import_symbol_name
                if suffix in extension_list and path.exists():
                    result_path = [path]
            else:
                result_path = _search_file(
                    importer_file_path.parent, import_symbol_name
                )
            return result_path
        else:
            return module_map.get(import_symbol_name, None)

    def resolve_python_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path] | None:
        assert import_symbol_node.type in (
            "import_statement",
            "import_from_statement",
        ), "import_symbol_node type is not import_statement or import_from_statement"

        source_path = str(importer_file_path)
        # source_path = None
        if import_symbol_node.type == "import_from_statement":
            module_name = import_symbol_node.child_by_field_name(
                "module_name"
            ).text.decode()
            asname = None
            if asname_node := import_symbol_node.child_by_field_name("name"):
                if (
                    asname_node.type == "aliased_import"
                    and asname_node.child_by_field_name("name")
                ):
                    asname = asname_node.child_by_field_name("name").text.decode()
                else:
                    asname = asname_node.text.decode()
            is_star = any(
                child.type == "wildcard_import" for child in import_symbol_node.children
            )
            name = f"{module_name}.{asname}" if asname else module_name
            imp = ImportStatement(name, asname, True, is_star, source_path)
        else:
            name = None
            asname = None
            if name_node := import_symbol_node.child_by_field_name("name"):
                if (
                    name_node.type == "aliased_import"
                    and name_node.child_by_field_name("name")
                ):
                    name = name_node.child_by_field_name("name").text.decode()
                    asname = name_node.child_by_field_name("alias").text.decode()
                else:
                    name = name_node.text.decode()
            imp = ImportStatement(name, asname, False, False, source_path)

        resolver = Resolver(self.repo.repo_path, importer_file_path)

        try:
            resolved_path = resolver.resolve_import(imp)
            return [resolved_path] if resolved_path else None
        except ImportException as e:
            logger.warn(f"Failed to resolve import: {e}")

    def resolve_php_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path] | None:
        import_symbol_name = import_symbol_node.text.decode()
        # Strip double and single quote
        import_symbol_name = import_symbol_name.strip('"').strip("'")
        # Find the module path
        result_path = []
        import_path = Path(import_symbol_name)
        if import_path.is_absolute() and import_path.exists():
            result_path.append(import_path)
        else:
            path = importer_file_path.parent / import_symbol_name
            if path.exists():
                result_path.append(path)
        return result_path

    def resolve_ruby_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path] | None:
        import_symbol_name = import_symbol_node.text.decode()
        # Strip double and single quote
        import_symbol_name = import_symbol_name.strip('"').strip("'")

        extension_list = Repository.code_file_extensions[Language.Ruby]

        # Find the module path
        result_path = []
        for ext in extension_list:
            import_path = Path(import_symbol_name).with_suffix(ext)
            if import_path.is_absolute() and import_path.exists():
                result_path.append(import_path)
            else:
                path = importer_file_path.parent / import_symbol_name
                path = path.with_suffix(ext)
                if path.exists():
                    result_path.append(path)

        return result_path

    def resolve_c_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path] | None:

        import_symbol_name = import_symbol_node.text.decode()
        # Strip double quote and angle bracket
        import_symbol_name = import_symbol_name.strip('"').lstrip("<").rstrip(">")
        import_path = Path(import_symbol_name)

        # Heuristics to search for the header file
        search_paths = [
            # Common practice to have headers in 'include' directory
            self.repo.repo_path / "include" / import_path,
            # Relative path from the C file's directory
            importer_file_path.parent / import_path,
            # Common practice to have headers in 'src' directory
            self.repo.repo_path / "src" / import_path,
            # Absolute/relative path as given in the include statement
            import_path,
        ]

        # Add parent directories of the C file path
        for parent in importer_file_path.parents:
            search_paths.append(parent / import_path)

        # Add sibling directories of each directory component of importer_file_path
        for parent in importer_file_path.parents:
            for sibling in parent.iterdir():
                if sibling.is_dir() and sibling != importer_file_path:
                    search_paths.append(sibling / import_path)

        # Find the module path
        result_path = []
        # Check if any of these paths exist
        for path in search_paths:
            if path.exists():
                result_path.append(path)

        return result_path
