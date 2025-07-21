from __future__ import annotations

from typing import TYPE_CHECKING

import tree_sitter_zig
from tree_sitter import Language, Parser

if TYPE_CHECKING:
    from tree_sitter import Node, Tree


class _ZigDocsExtractor:
    ZIG_LANGUAGE = Language(tree_sitter_zig.language())

    def __init__(self):
        self.parser = Parser(self.ZIG_LANGUAGE)

    def get_docs(self, code: str) -> dict:
        tree = self.parser.parse(bytes(code, "utf8"))
        return {
            "docstring": "\n".join(self._get_module_docs(tree, code)),
            "functions": self._get_functions(tree, code),
            "constants": self._get_constants(tree, code),
            "structs": self._get_structures(tree, code),
        }

    def _get_module_docs(self, tree: Tree, code: str) -> list:
        """Extract //! module-level docs."""
        docs = []
        root = tree.root_node

        for node in root.children:
            if node.type == "comment":
                text = self._get_node_text(node, code)
                if text.startswith("//!"):
                    docs.append(text[3:].strip())

        return docs

    def _get_functions(self, tree: Tree, code: str) -> list:
        """Extract functions with /// docs."""
        functions = []
        root = tree.root_node

        for node in root.children:
            if node.type == "function_declaration":
                fn_name = None
                doc_comments = []

                # Get preceding comments
                prev = node.prev_named_sibling
                while prev and prev.type == "comment":
                    text = self._get_node_text(prev, code)
                    if text.startswith("///"):
                        doc_comments.insert(0, text[3:].strip())
                    prev = prev.prev_named_sibling

                # Get function name
                for child in node.children:
                    if child.type == "identifier":
                        fn_name = self._get_node_text(child, code)
                        break

                if fn_name:
                    functions.append(
                        {
                            "name": fn_name,
                            "docstring": "\n".join(doc_comments),
                            "signature": self._get_node_text(node, code)
                            .split("{")[0]
                            .strip(),
                        },
                    )

        return functions

    def _get_constants(self, tree: Tree, code: str) -> list:
        """Extract constants with /// docs."""
        constants = []
        root = tree.root_node

        for node in root.children:
            if (
                node.type == "variable_declaration"
                and "struct" not in self._get_node_text(node, code)
            ):
                # Skip imports (@import or std.import-like patterns)
                if self._is_import(node, code):
                    continue

                const_name = None
                doc_comments = []

                # Get preceding docs
                prev = node.prev_named_sibling
                while prev and prev.type == "comment":
                    text = self._get_node_text(prev, code)
                    if text.startswith("///"):
                        doc_comments.insert(0, text[3:].strip())
                    prev = prev.prev_named_sibling

                # Get constant name
                for child in node.children:
                    if child.type == "identifier":
                        const_name = self._get_node_text(child, code)
                        break

                if const_name:
                    constants.append(
                        {
                            "name": const_name,
                            "docstring": "\n".join(doc_comments),
                        },
                    )

        return constants

    def _is_import(self, node: Node, code: str) -> bool:
        node_text = self._get_node_text(node, code)

        # Common import patterns
        import_patterns = ["= @import(", ".import("]

        return any(pattern in node_text for pattern in import_patterns)

    def _get_node_text(self, node: Node, code: str) -> str:
        """Extract source text for a node."""
        return code[node.start_byte : node.end_byte]

    def _get_structures(self, tree: Tree, code: str) -> list:
        """Extract struct definitions with documentation."""
        structures = []
        root = tree.root_node

        for node in root.children:
            if node.type == "variable_declaration" and "struct" in self._get_node_text(node, code):
                struct_name = None
                doc_comments = []

                # Get preceding documentation
                prev = node.prev_named_sibling
                while prev and prev.type == "comment":
                    text = self._get_node_text(prev, code)
                    if text.startswith("///"):
                        doc_comments.insert(0, text[3:].strip())
                    prev = prev.prev_named_sibling

                # Extract struct name
                for child in node.children:
                    if child.type == "identifier":
                        struct_name = self._get_node_text(child, code)
                        break

                if struct_name:
                    # Get struct fields
                    fields = []
                    struct_body = node.child_by_field_name("value")
                    if struct_body:
                        for field_node in struct_body.named_children:
                            if field_node.type == "field_declaration":
                                field_name = ""
                                field_type = ""
                                for child in field_node.children:
                                    if child.type == "identifier":
                                        field_name = self._get_node_text(child, code)
                                    elif child.type == "type_expression":
                                        field_type = self._get_node_text(child, code)

                                if field_name and field_type:
                                    fields.append(
                                        {"name": field_name, "type": field_type},
                                    )

                    structures.append(
                        {
                            "name": struct_name,
                            "docstring": "\n".join(doc_comments),
                            # "fields": fields,
                        },
                    )

        return structures
