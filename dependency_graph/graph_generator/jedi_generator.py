import re
import traceback

import jedi
from jedi.api.classes import Name, BaseName
from parso.python.tree import Name as ParsoTreeName
from parso.tree import BaseNode

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import (
    BaseDependencyGraphGenerator,
    DependencyGraphGeneratorType,
)
from dependency_graph.models import PathLike
from dependency_graph.models.graph_data import (
    Location,
    Node,
    EdgeRelation,
    Edge,
    NodeType,
)
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()

# Mapping from jedi api type to node type
_JEDI_API_TYPES_dict: dict[str, NodeType | None] = {
    "module": NodeType.MODULE,
    "class": NodeType.CLASS,
    "instance": NodeType.VARIABLE,
    "function": NodeType.FUNCTION,
    "param": NodeType.VARIABLE,
    "path": NodeType.MODULE,
    "keyword": None,
    "property": NodeType.VARIABLE,
    "statement": NodeType.STATEMENT,
    "namespace": NodeType.MODULE,
}


class JediDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (Language.Python,)

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def _convert_name_pos_to_location(
        self, name: Name, node_type: NodeType | None = None
    ) -> Location | None:
        """helper function for creating location"""
        if name is None:
            return None

        location_params = {"file_path": name.module_path}

        if node_type and node_type == NodeType.MODULE:
            start_pos = name._name.get_root_context()._value.tree_node.start_pos
            end_pos = name._name.get_root_context()._value.tree_node.end_pos
        else:
            start_pos = name.get_definition_start_position()
            end_pos = name.get_definition_end_position()

        if start_pos:
            location_params.update(
                start_line=start_pos[0],
                start_column=start_pos[1] + 1,  # Convert to 1-based indexing
            )

        if end_pos:
            location_params.update(
                end_line=end_pos[0],
                end_column=end_pos[1] + 1,  # Convert to 1-based indexing
            )
        return Location(**location_params)

    def _convert_name_to_node(self, name: Name, node_type: NodeType) -> Node:
        """helper function for creating nodes"""
        location = self._convert_name_pos_to_location(name, node_type)

        node_name = name.name
        # Add class name to the method's node name
        if name.type == "function" and name.parent() and name.parent().type == "class":
            node_name = f"{name.parent().name}.{name.name}"

        return Node(
            type=node_type,
            name=node_name,
            location=location,
        )

    def _update_graph(
        self,
        D: DependencyGraph,
        from_name: Name,
        from_type: NodeType,
        to_name: Name,
        to_type: NodeType,
        edge_name: Name
        | None,  # Edge name can be None as not all relation have a location
        edge_relation: EdgeRelation,
        inverse_edge_relation: EdgeRelation,
    ):
        """helper function for updating the graph"""
        from_node = self._convert_name_to_node(from_name, from_type)
        to_node = self._convert_name_to_node(to_name, to_type)

        edge_location = self._convert_name_pos_to_location(edge_name)
        D.add_relational_edge(
            from_node,
            to_node,
            Edge(relation=edge_relation, location=edge_location),
            Edge(relation=inverse_edge_relation, location=edge_location),
        )

    def _extract_parent_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            try:
                # # TODO missing adding global variable
                # if name.type not in (
                #     "class",
                #     "function",
                # ):
                #     continue

                definitions = name.goto(
                    follow_imports=True, follow_builtin_imports=False
                )
                if not definitions:
                    continue

                parent = name.parent()
                for definition in definitions:
                    # Skip builtin
                    # Skip definition that are not in the same file
                    if (
                        definition.in_builtin_module()
                        or not definition.module_path == script.path
                    ):
                        continue

                    self._update_graph(
                        D=D,
                        from_name=parent,
                        from_type=_JEDI_API_TYPES_dict[parent.type],
                        to_name=name,
                        # TODO what if _JEDI_API_TYPES_dict doesn't have the key ?
                        to_type=_JEDI_API_TYPES_dict[name.type],
                        edge_name=None,
                        edge_relation=EdgeRelation.ParentOf,
                        inverse_edge_relation=EdgeRelation.ChildOf,
                    )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting parent relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _extract_import_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            try:
                definitions = name.goto(
                    follow_imports=True, follow_builtin_imports=False
                )
                if not definitions:
                    continue

                for definition in definitions:
                    # If the definition's parent is not a module, it means it is not importable
                    if definition.parent() and definition.parent().type not in (
                        "module",
                        "namespace",
                    ):
                        continue

                    # Skip instantiation, this should be dealt with in the instantiate relation
                    if definition.type == "instance":
                        continue

                    # Skip definition that are in the same file
                    if definition.module_path == script.path:
                        continue

                    # Use the helper function to update the graph
                    self._update_graph(
                        D=D,
                        from_name=script.get_context(),
                        from_type=NodeType.MODULE,
                        to_name=definition,
                        to_type=NodeType.VARIABLE
                        if definition.type == "statement"
                        else _JEDI_API_TYPES_dict[definition.type],
                        edge_name=name,
                        edge_relation=EdgeRelation.Imports,
                        inverse_edge_relation=EdgeRelation.ImportedBy,
                    )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting import relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _extract_call_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            try:
                callers = name.goto(follow_imports=True, follow_builtin_imports=True)
                if not callers:
                    continue

                for callee in callers:
                    if callee.type != "function":
                        continue

                    # Find caller, caller should be a function, or a module (call under `if __name__ == "__main__"`)
                    if name.parent().type not in ("function", "module", "namespace"):
                        continue
                    caller = name.parent()

                    # Use the helper function to update the graph
                    self._update_graph(
                        D=D,
                        from_name=caller,
                        from_type=_JEDI_API_TYPES_dict[caller.type],
                        to_name=callee,
                        to_type=_JEDI_API_TYPES_dict[callee.type],
                        edge_name=name,
                        edge_relation=EdgeRelation.Calls,
                        inverse_edge_relation=EdgeRelation.CalledBy,
                    )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting call relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _extract_instantiate_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            try:
                if name.type not in ("statement",):
                    continue

                # Skip self
                if name.name == "self":
                    continue

                if name.parent().type not in (
                    "class",
                    "module",
                    "function",
                    "namespace",
                ):
                    continue

                instance_type_names = name.goto()
                if not instance_type_names:
                    continue

                instance_types = []
                # Instance_type is the type of the instance
                for instance_type in instance_type_names:
                    # Resolve the instance_type if it is an import statement
                    if instance_type._name and instance_type._name.is_import():
                        tmp_names = instance_type.goto()
                        if not tmp_names:
                            continue
                        instance_types.extend(tmp_names)
                    else:
                        instance_types.append(instance_type)

                for instance_type in instance_types:
                    # Skip builtin types
                    if instance_type.in_builtin_module():
                        continue

                    if instance_type.type == "param":
                        continue

                    # We only accept class type as an instance for now
                    if instance_type.type not in ("class",):
                        continue

                    instance_owner = name.parent()
                    if instance_owner.type == "module":
                        # the instance owner is a module, try to find if the actual owner is a global variable
                        expr_stmt_node: BaseNode = name._name.tree_name.search_ancestor(
                            "expr_stmt"
                        )
                        if expr_stmt_node and len(expr_stmt_node.children) > 0:
                            if isinstance(expr_stmt_node.children[0], ParsoTreeName):
                                instance_owner = BaseName(
                                    instance_type._inference_state,
                                    script._get_module_context().create_name(
                                        expr_stmt_node.children[0]
                                    ),
                                )

                    # Use the helper function to update the graph
                    self._update_graph(
                        D=D,
                        from_name=instance_owner,
                        from_type=NodeType.VARIABLE
                        if instance_owner.type == "statement"
                        else _JEDI_API_TYPES_dict[instance_owner.type],
                        to_name=instance_type,
                        to_type=_JEDI_API_TYPES_dict[instance_type.type],
                        # Instantiate name is the name that is being instantiated
                        edge_name=name,
                        edge_relation=EdgeRelation.Instantiates,
                        inverse_edge_relation=EdgeRelation.InstantiatedBy,
                    )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting instantiate relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _extract_def_use_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            try:
                if name._name.is_import():
                    continue

                references = script.get_references(name.line, name.column)
                for ref in references:  # type: Name
                    if ref == name:
                        continue

                    if ref.line is None:
                        continue

                    # Kill previous definitions
                    if ref.line < name.line or (
                        ref.line == name.line and ref.column < name.column
                    ):
                        continue

                    self._update_graph(
                        D=D,
                        from_name=name,
                        from_type=_JEDI_API_TYPES_dict[name.type],
                        to_name=ref,
                        to_type=_JEDI_API_TYPES_dict[ref.type],
                        edge_name=None,
                        edge_relation=EdgeRelation.Defines,
                        inverse_edge_relation=EdgeRelation.DefinedBy,
                    )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting def-use relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _extract_class_hierarchy_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        def get_parent_classes_with_columns(class_definition: str) -> dict[str, int]:
            """
            Get the parent classes and their columns in the class definition header
            e.g.
            "class Child(object, A, B):" will return {'object': 12, 'A': 20, 'B': 23}
            """
            # Regex to find the class header
            class_header_regex = r"class\s+\w+\(([^)]+)\):"

            # Regex to match class names
            class_name_regex = r"\b\w+\b"

            # Find the class header
            header_match = re.search(class_header_regex, class_definition)
            if not header_match:
                return {}

            parent_class_string = header_match.group(1)

            # Find the parent class names and their columns
            parent_classes_with_columns = {}

            for match in re.finditer(class_name_regex, parent_class_string):
                # Column = start index of match within the class header + offset up to the opening parenthesis
                column_number = match.start() + header_match.start(1)
                class_name = match.group()
                parent_classes_with_columns[class_name] = column_number

            return parent_classes_with_columns

        for name in all_names:
            try:
                if name.type != "class":
                    continue

                class_header = name.get_line_code()
                parent_classes_with_columns = get_parent_classes_with_columns(
                    class_header
                )

                for column_index in parent_classes_with_columns.values():
                    references = script.get_references(name.line, column_index)

                    edge_names = script.goto(name.line, column_index)
                    edge_name = None
                    if edge_names:
                        edge_name = edge_names[0]

                    # Deduplicate the references
                    ref_set = set()
                    for ref in references:  # type: Name
                        if ref.type == "class":
                            ref_set.update(ref.goto())

                    for ref in ref_set:
                        self._update_graph(
                            D=D,
                            from_name=name,
                            from_type=_JEDI_API_TYPES_dict[name.type],
                            to_name=ref,
                            to_type=_JEDI_API_TYPES_dict[ref.type],
                            edge_name=edge_name,
                            edge_relation=EdgeRelation.DerivedClassOf,
                            inverse_edge_relation=EdgeRelation.BaseClassOf,
                        )
            except Exception as e:
                tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                logger.error(
                    f"Error while extracting def-use relation for name {name} in {name.module_path}: Error {e} occurred at:\n{tb_str}"
                )

    def _generate_file(
        self,
        code: str,
        file_path: PathLike,
        D: DependencyGraph,
        project: jedi.Project = None,
    ):
        try:
            script = jedi.Script(
                code,
                path=file_path,
                project=project,
            )

            all_def_names = script.get_names(
                all_scopes=True, definitions=True, references=False
            )
            self._extract_parent_relation(script, all_def_names, D)
            self._extract_import_relation(script, all_def_names, D)
            self._extract_def_use_relation(script, all_def_names, D)
            self._extract_class_hierarchy_relation(script, all_def_names, D)

            all_ref_names = script.get_names(
                all_scopes=True, definitions=False, references=True
            )
            self._extract_call_relation(script, all_ref_names, D)
            self._extract_instantiate_relation(script, all_ref_names, D)
        except Exception as e:
            tb_str = "\n".join(traceback.format_tb(e.__traceback__))
            logger.error(
                f"Error while generating graph of type {DependencyGraphGeneratorType.JEDI.value} for {file_path}, will ignore it. Error {e} occurred at:\n{tb_str}"
            )

    def generate_file(
        self,
        repo: Repository,
        code: str = None,
        file_path: PathLike = None,
    ) -> DependencyGraph:
        if code is None and file_path is None:
            raise ValueError("Must provide at least one of code or file_path")

        project = jedi.Project(repo.repo_path, load_unsafe_extensions=False)

        D = DependencyGraph(repo.repo_path, repo.language)
        self._generate_file(code, file_path, D, project)
        return D

    def generate(self, repo: Repository) -> DependencyGraph:
        project = jedi.Project(repo.repo_path, load_unsafe_extensions=False)

        D = DependencyGraph(repo.repo_path, repo.language)
        for file in repo.files:
            if not file.content.strip():
                continue
            self._generate_file(file.content, file.file_path, D, project)

        return D
