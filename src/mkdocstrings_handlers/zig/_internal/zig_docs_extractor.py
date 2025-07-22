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

                fn_name = self._get_node_name(node)
                doc_comment = self._get_doc_comments(node)
                if fn_name and doc_comment:
                    functions.append(
                        {
                            "name": fn_name,
                            "doc": doc_comment,
                            "signature": self._get_function_signature(node),
                        },
                    )

        return functions

    def _get_function_signature(self, node: Node) -> str:
        """Extract signature of the function."""
        return self._get_node_text(node).split("{")[0].strip()

    def _get_node_name(self, node: Node) -> str | None:
        """Get node identifier as it's name."""
        for child in node.children:
            if child.type in ("identifier", "builtin_identifier"):
                return self._get_node_text(child)

        return None

    def _get_constants(self) -> list:
        """Extract constants with /// docs."""
        constants = []
        root = self.tree.root_node

        for node in root.children:
            if node.type == "variable_declaration":
                if self._is_import(node) or self._is_struct(node):
                    continue

                const_name = self._get_node_name(node)
                doc = self._get_doc_comments(node)
                if const_name and doc:
                    constants.append({"name": const_name, "doc": doc})

        return constants

    def _is_import(self, node: Node) -> bool:
        """Check if the given constant is an import."""
        for child in node.children:
            if child.type == "builtin_function" and self._get_node_name(child) == "@import":
                return True

        return False

    def _is_struct(self, node: Node) -> bool:
        """Check if the given constant is a structure."""
        return any(child.type == "struct_declaration" for child in node.children)

    def _get_node_text(self, node: Node) -> str:
        """Extract source text for a node."""
        return self.code[node.start_byte : node.end_byte].decode("utf-8")

    def _get_structures(self) -> list:
        """Extract struct definitions with documentation."""
        structures = []
        root = self.tree.root_node

        for node in root.children:
            if node.type == "variable_declaration" and self._is_struct(node):
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
        """Extract preceding doc comments."""
        doc_comments = []

        prev = node.prev_named_sibling
        while prev and prev.type == "comment":
            text = self._get_node_text(prev)
            if text.startswith("///"):
                doc_comments.insert(0, text[3:].strip())
            prev = prev.prev_named_sibling

        return "\n".join(doc_comments)

    def _get_structure_fields(self, node: Node) -> list:
        """Extract structure fields."""
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

    fn notDocumented() void {
    }

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
