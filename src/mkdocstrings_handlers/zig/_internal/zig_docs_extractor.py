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
        code_bytes = code.encode("utf-8")
        tree = self.parser.parse(code_bytes)
        return {
            "docstring": "\n".join(self._get_module_docs(tree, code_bytes)),
            "functions": self._get_functions(tree, code_bytes),
            "constants": self._get_constants(tree, code_bytes),
            "structs": self._get_structures(tree, code_bytes),
        }

    def _get_module_docs(self, tree: Tree, code: bytes) -> list:
        """Extract //! module-level docs."""
        docs = []
        root = tree.root_node

        for node in root.children:
            if node.type == "comment":
                text = self._get_node_text(node, code)
                if text.startswith("//!"):
                    docs.append(text[3:].strip())

        return docs

    def _get_functions(self, tree: Tree, code: bytes) -> list:
        """Extract functions with /// docs."""
        functions = []
        root = tree.root_node

        for node in root.children:
            if node.type == "function_declaration":
                fn_name = None

                # Get function name
                for child in node.children:
                    if child.type == "identifier":
                        fn_name = self._get_node_text(child, code)
                        break

                if fn_name:
                    functions.append(
                        {
                            "name": fn_name,
                            "docstring": self._get_doc_comments(node, code),
                            "signature": self._get_node_text(node, code)
                            .split("{")[0]
                            .strip(),
                        },
                    )

        return functions

    def _get_constants(self, tree: Tree, code: bytes) -> list:
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

                # Get constant name
                for child in node.children:
                    if child.type == "identifier":
                        const_name = self._get_node_text(child, code)
                        break

                if const_name:
                    constants.append(
                        {
                            "name": const_name,
                            "docstring": self._get_doc_comments(node, code),
                        },
                    )

        return constants

    def _is_import(self, node: Node, code: bytes) -> bool:
        node_text = self._get_node_text(node, code)

        # Common import patterns
        import_patterns = ["= @import(", ".import("]

        return any(pattern in node_text for pattern in import_patterns)

    def _get_node_text(self, node: Node, code: bytes) -> str:
        """Extract source text for a node."""
        return code[node.start_byte : node.end_byte].decode("utf-8")

    def _get_structures(self, tree: Tree, code: bytes) -> list:
        """Extract struct definitions with documentation."""
        structures = []
        root = tree.root_node

        for node in root.children:
            if node.type == "variable_declaration" and "struct" in self._get_node_text(
                node, code,
            ):
                struct_name = None

                # Extract struct name
                for child in node.children:
                    if child.type == "identifier":
                        struct_name = self._get_node_text(child, code)
                        break

                if not struct_name:
                    continue

                structures.append(
                    {
                        "name": struct_name,
                        "docstring": self._get_doc_comments(node, code),
                        "fields": self._get_structure_fields(node, code),
                    },
                )

        return structures

    def _get_doc_comments(self, node: Node, code: bytes) -> str:
        doc_comments = []

        prev = node.prev_named_sibling
        while prev and prev.type == "comment":
            text = self._get_node_text(prev, code)
            if text.startswith("///"):
                doc_comments.insert(0, text[3:].strip())
            prev = prev.prev_named_sibling

        return "\n".join(doc_comments)

    def _get_structure_fields(self, node: Node, code: bytes) -> list:
        # Get struct fields
        fields = []

        for child in node.children:
            if child.type == "struct_declaration":
                break
        else:
            return []

        for field_node in child.named_children:
            if field_node.type == "container_field":
                field_name = ""
                field_type = ""
                for child in field_node.children:
                    if child.type == "identifier":
                        field_name = self._get_node_text(child, code)
                    elif child.type == ":":
                        continue
                    else:
                        field_type = self._get_node_text(child, code)
                        break

                if field_name and field_type:
                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "docstring": self._get_doc_comments(field_node, code),
                        },
                    )

        return fields


def _main() -> None:
    import json  # noqa: PLC0415

    code = """
    /// A spreadsheet position
    pub const Pos = struct {
        /// (0-indexed) row
        x: u32,
        /// (0-indexed) column
        y: u32,

        /// The top-left position
        pub const zero: Pos = .{ .x = 0, .y = 0 };

        /// Illegal position
        pub const invalid_pos: Pos = .{
            .x = std.math.maxInt(u32),
            .y = std.math.maxInt(u32),
        };
    };
    """

    extractor = _ZigDocsExtractor()
    print(json.dumps(extractor.get_docs(code), indent=4))  # noqa: T201


if __name__ == "__main__":
    _main()
