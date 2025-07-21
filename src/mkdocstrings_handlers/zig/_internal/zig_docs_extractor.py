from __future__ import annotations

from typing import TYPE_CHECKING

import tree_sitter_zig
from tree_sitter import Language, Parser

if TYPE_CHECKING:
    from tree_sitter import Node, Tree


class _ZigDocsExtractor:
    ZIG_LANGUAGE = Language(tree_sitter_zig.language())
    parser = Parser(ZIG_LANGUAGE)

    code: bytes
    tree: Tree

    def __init__(self, code: str):
        self.code = code.encode("utf-8")
        self.tree = self.parser.parse(self.code)

    def get_docs(self) -> dict:
        return {
            "doc": "\n".join(self._get_module_docs()),
            "functions": self._get_functions(),
            "constants": self._get_constants(),
            "structs": self._get_structures(),
        }

    def _get_module_docs(self) -> list:
        """Extract //! module-level docs."""
        docs = []
        root = self.tree.root_node

        for node in root.children:
            if node.type == "comment":
                text = self._get_node_text(node)
                if text.startswith("//!"):
                    docs.append(text[3:].strip())

        return docs

    def _get_functions(self) -> list:
        """Extract functions with /// docs."""
        functions = []
        root = self.tree.root_node

        for node in root.children:
            if node.type == "function_declaration":
                fn_name = None

                # Get function name
                for child in node.children:
                    if child.type == "identifier":
                        fn_name = self._get_node_text(child)
                        break

                if fn_name:
                    functions.append(
                        {
                            "name": fn_name,
                            "doc": self._get_doc_comments(node),
                            "signature": self._get_node_text(node)
                            .split("{")[0]
                            .strip(),
                        },
                    )

        return functions

    def _get_node_name(self, node: Node) -> str | None:
        for child in node.children:
            if child.type in ("identifier", "builtin_identifier"):
                return self._get_node_text(child)

        return None

    def _get_constants(self) -> list:
        """Extract constants with /// docs."""
        constants = []
        root = self.tree.root_node

        for node in root.children:
            if (
                node.type == "variable_declaration"
                and "struct" not in self._get_node_text(node)
            ):
                if self._is_import(node):
                    continue

                const_name = self._get_node_name(node)
                if const_name:
                    constants.append(
                        {
                            "name": const_name,
                            "doc": self._get_doc_comments(node),
                        },
                    )

        return constants

    def _is_import(self, node: Node) -> bool:
        for child in node.children:
            if child.type == "builtin_function" and self._get_node_name(child) == "@import":
                return True

        return False

    def _get_node_text(self, node: Node) -> str:
        """Extract source text for a node."""
        return self.code[node.start_byte : node.end_byte].decode("utf-8")

    def _get_structures(self) -> list:
        """Extract struct definitions with documentation."""
        structures = []
        root = self.tree.root_node

        for node in root.children:
            if node.type == "variable_declaration" and "struct" in self._get_node_text(node):
                struct_name = self._get_node_name(node)
                if not struct_name:
                    continue

                structures.append(
                    {
                        "name": struct_name,
                        "doc": self._get_doc_comments(node),
                        "fields": self._get_structure_fields(node),
                    },
                )

        return structures

    def _get_doc_comments(self, node: Node) -> str:
        doc_comments = []

        prev = node.prev_named_sibling
        while prev and prev.type == "comment":
            text = self._get_node_text(prev)
            if text.startswith("///"):
                doc_comments.insert(0, text[3:].strip())
            prev = prev.prev_named_sibling

        return "\n".join(doc_comments)

    def _get_structure_fields(self, node: Node) -> list:
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
                        field_name = self._get_node_text(child)
                    elif child.type == ":":
                        continue
                    else:
                        field_type = self._get_node_text(child)
                        break

                if field_name and field_type:
                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "doc": self._get_doc_comments(field_node),
                        },
                    )

        return fields


def _main() -> None:
    import json  # noqa: PLC0415

    code = """
    const std = @import("std");

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

    extractor = _ZigDocsExtractor(code)
    print(json.dumps(extractor.get_docs(), indent=4))  # noqa: T201


if __name__ == "__main__":
    _main()
