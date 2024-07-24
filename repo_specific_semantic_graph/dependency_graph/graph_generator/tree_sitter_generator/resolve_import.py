import os
from pathlib import Path

from importlab.parsepy import ImportStatement
from importlab.resolve import ImportException
from tree_sitter import Node as TS_Node

from dependency_graph.graph_generator.tree_sitter_generator.python_resolver import (
    Resolver,
)
from dependency_graph.models import VirtualPath, PathLike
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


class ImportResolver:
    def __init__(self, repo: Repository):
        self.repo = repo

    def _Path(self, file_path: PathLike) -> Path:
        """
        Convert the str file path to handle both physical and virtual paths
        """
        match self.repo.repo_path:
            case Path():
                return Path(file_path)
            case VirtualPath():
                return VirtualPath(self.repo.repo_path.fs, file_path)
            case _:
                return Path(file_path)

    def resolve_import(
        self,
        import_symbol_node: TS_Node,
        module_map: dict[str, list[Path]],
        importer_file_path: Path,
    ) -> list[Path] | None:
        resolved_path_list = []

        match self.repo.language:
            case Language.Java | Language.Kotlin:
                import_symbol_name = import_symbol_node.text.decode()
                # Deal with star import: `import xxx.*`
                if b".*" in import_symbol_node.parent.text:
                    for module_name, path_list in module_map.items():
                        # Use rpartition to split the string at the rightmost '.'
                        package_name, _, _ = module_name.rpartition(".")
                        if package_name == import_symbol_name:
                            resolved_path_list.extend(path_list)
                else:
                    resolved_path_list.extend(module_map.get(import_symbol_name, []))
            case Language.CSharp:
                import_symbol_name = import_symbol_node.text.decode()
                resolved_path_list.extend(module_map.get(import_symbol_name, []))
            case Language.TypeScript | Language.JavaScript:
                resolved_path_list.extend(
                    self.resolve_ts_js_import(
                        import_symbol_node, module_map, importer_file_path
                    )
                )
            case Language.Python:
                resolved_path_list.extend(
                    self.resolve_python_import(import_symbol_node, importer_file_path)
                )
            case Language.PHP:
                resolved_path_list.extend(
                    self.resolve_php_import(import_symbol_node, importer_file_path)
                )
            case Language.Ruby:
                resolved_path_list.extend(
                    self.resolve_ruby_import(import_symbol_node, importer_file_path)
                )
            case Language.C | Language.CPP:
                resolved_path_list.extend(
                    self.resolve_cfamily_import(import_symbol_node, importer_file_path)
                )
            case Language.Go:
                resolved_path_list.extend(self.resolve_go_import(import_symbol_node))
            case Language.Swift:
                resolved_path_list.extend(
                    self.resolve_swift_import(import_symbol_node, importer_file_path)
                )
            case _:
                raise NotImplementedError(
                    f"Language {self.repo.language} is not supported"
                )

        # De-duplicate the resolved path
        return list(set(resolved_path_list))

    def resolve_ts_js_import(
        self,
        import_symbol_node: TS_Node,
        module_map: dict[str, list[Path]],
        importer_file_path: Path,
    ) -> list[Path]:
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
            result_path = []
            # If there is a suffix in the name
            if suffix := self._Path(import_symbol_name).suffix:
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
            return module_map.get(import_symbol_name, [])

    def resolve_python_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path]:
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
            return [resolved_path] if resolved_path else []
        except ImportException as e:
            logger.warn(f"Failed to resolve import: {e}")
            return []

    def resolve_php_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path]:
        import_symbol_name = import_symbol_node.text.decode()
        # Strip double and single quote
        import_symbol_name = import_symbol_name.strip('"').strip("'")
        # Find the module path
        result_path = []
        import_path = self._Path(import_symbol_name)
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
    ) -> list[Path]:
        import_symbol_name = import_symbol_node.text.decode()
        # Strip double and single quote
        import_symbol_name = import_symbol_name.strip('"').strip("'")

        extension_list = Repository.code_file_extensions[Language.Ruby]

        # Find the module path
        result_path = []
        for ext in extension_list:
            import_path = self._Path(import_symbol_name).with_suffix(ext)
            if import_path.is_absolute() and import_path.exists():
                result_path.append(import_path)
            else:
                path = importer_file_path.parent / import_symbol_name
                path = path.with_suffix(ext)
                if path.exists():
                    result_path.append(path)

        return result_path

    def resolve_cfamily_import(
        self,
        import_symbol_node: TS_Node,
        importer_file_path: Path,
    ) -> list[Path]:

        import_symbol_name = import_symbol_node.text.decode()
        # Strip double quote and angle bracket
        import_symbol_name = import_symbol_name.strip('"').lstrip("<").rstrip(">")
        import_path = self._Path(import_symbol_name)

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

    def resolve_go_import(self, import_symbol_node: TS_Node) -> list[Path]:
        def parse_go_mod(go_mod_path: Path):
            module_path = None
            replacements = {}

            for line in go_mod_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("module "):
                    module_path = line.split()[1]
                elif line.startswith("replace "):
                    parts = line.split()
                    if len(parts) >= 4 and parts[2] == "=>":
                        replacements[parts[1]] = parts[3]

            return module_path, replacements

        def search_fallback_paths(import_stmt: str, base_path: Path):
            """Searches various fallback paths within the project directory."""
            search_paths = [
                base_path / import_stmt.replace("/", os.sep),
                base_path / "src" / import_stmt.replace("/", os.sep),
                base_path / "vendor" / import_stmt.replace("/", os.sep),
                base_path / "pkg" / import_stmt.replace("/", os.sep),
            ]
            found_files = []

            for path in search_paths:
                if path.is_dir():
                    go_files = list(path.glob("*.go"))
                    if go_files:
                        found_files.extend(go_files)
                elif path.with_suffix(".go").is_file():
                    found_files.append(path.with_suffix(".go"))

            return found_files

        # Parse the go.mod file
        go_mod_path = self.repo.repo_path / "go.mod"
        if go_mod_path.exists():
            module_path, replacements = parse_go_mod(go_mod_path)
        else:
            module_path, replacements = None, {}

        # Find corresponding paths for the imported packages
        imported_paths = []

        import_stmt = import_symbol_node.text.decode()
        import_stmt = import_stmt.strip('"')

        # Resolve the import path using replacements or the module path
        resolved_paths = []
        if import_stmt in replacements:
            resolved_path = replacements[import_stmt]
            resolved_paths.append(resolved_path)
        elif module_path and import_stmt.startswith(module_path):
            resolved_path = self.repo.repo_path / import_stmt[len(module_path) + 1 :]
            resolved_paths.append(resolved_path)
        else:
            # Fallback logic: Try to resolve based on project directory structure
            resolved_paths.extend(
                search_fallback_paths(import_stmt, self.repo.repo_path)
            )

        for resolved_path in resolved_paths:
            if resolved_path:
                if resolved_path.is_dir():
                    # Try to find a .go file in the directory
                    go_files = list(resolved_path.glob("*.go"))
                    if go_files:
                        imported_paths.extend(go_files)

        return imported_paths

    def resolve_swift_import(
        self, import_symbol_node: TS_Node, importer_file_path: Path
    ) -> list[Path]:
        import_symbol_name = import_symbol_node.text.decode()
        if len(import_symbol_node.parent.children) > 2:
            # Handle individual declarations importing such as `import kind module.symbol`
            # In this case, we extract the module name from the import statement
            import_symbol_name = (
                ".".join(import_symbol_name.split(".")[:-1])
                if "." in import_symbol_name
                else import_symbol_name
            )

        import_symbol_name = import_symbol_name.replace(".", os.sep)
        import_path = self._Path(import_symbol_name)

        # Heuristic search for source files corresponding to the imported modules
        search_paths = [
            self.repo.repo_path / "Sources" / import_symbol_name,
            self.repo.repo_path / "Tests" / import_symbol_name,
            self.repo.repo_path / "Modules" / import_symbol_name,
        ]

        # Add parent directories of the Swift file path
        for parent in importer_file_path.parents:
            search_paths.append(parent / import_path)

        # Add sibling directories of each directory component of importer_file_path
        for parent in importer_file_path.parents:
            for sibling in parent.iterdir():
                if sibling.is_dir() and sibling != importer_file_path:
                    search_paths.append(sibling / import_path)

        # Heuristic search for source files corresponding to the imported modules
        result_files = []

        for path in search_paths:
            extension_list = Repository.code_file_extensions[Language.Swift]
            if path.exists() and path.is_dir():
                for ext in extension_list:
                    for swift_file in path.glob(f"**/*{ext}"):
                        result_files.append(swift_file)

        # Return list of Path objects corresponding to the imported files
        return result_files
