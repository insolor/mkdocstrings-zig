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
        return self._parse_structure(self.tree.root_node)

    def _parse_structure(self, node: Node) -> dict:
        """Parse structure docs. A module is a structure too."""
        module_doc = []
        fields = []
        functions = []
        constants = []
        structs = []

        for child in node.children:
            if child.type == "comment":
                text = self._get_node_text(child)
                if text.startswith("//!"):
                    module_doc.append(text[3:].strip())
            if child.type == "container_field":
                field = self._parse_field(child)
                if field:
                    fields.append(field)
            elif child.type == "function_declaration":
                function = self._parse_function(child)
                if function:
                    functions.append(function)
            elif child.type == "variable_declaration":
                if self._is_import(child):
                    continue

                name = self._get_node_name(child)
                if not name:
                    continue

                doc = self._get_doc_comments(child)
                struct_node = self._get_struct_declaration(child)
                if struct_node:
                    structs.append(
                        {
                            "name": name,
                            "doc": doc,
                            **self._parse_structure(struct_node),
                        },
                    )
                elif doc:
                    constants.append({"name": name, "doc": doc})

        result = {}
        if module_doc:
            result["doc"] = "\n".join(module_doc)

        if fields:
            result["fields"] = fields

        if functions:
            result["functions"] = functions

        if constants:
            result["constants"] = constants

        if structs:
            result["structs"] = structs

        return result

    def _parse_function(self, node: Node) -> dict | None:
        """Parse function information."""
        fn_name = None

        fn_name = self._get_node_name(node)
        doc_comment = self._get_doc_comments(node)
        if fn_name and doc_comment:
            return {
                "name": fn_name,
                "doc": doc_comment,
                "signature": self._get_function_signature(node),
            }

        return None

    def _get_function_signature(self, node: Node) -> str:
        """Extract signature of the function."""
        return self._get_node_text(node).split("{")[0].strip()

    def _get_node_name(self, node: Node) -> str | None:
        """Get node identifier as it's name."""
        for child in node.children:
            if child.type in ("identifier", "builtin_identifier"):
                return self._get_node_text(child)

        return None

    def _is_import(self, node: Node) -> bool:
        """Check if the given constant is an import."""
        for child in node.children:
            if child.type == "builtin_function" and self._get_node_name(child) == "@import":
                return True

        return False

    def _get_node_text(self, node: Node) -> str:
        """Extract source text for a node."""
        return self.code[node.start_byte : node.end_byte].decode("utf-8")

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

    def _get_struct_declaration(self, node: Node) -> Node | None:
        """Extract struct declaration node."""
        for child in node.children:
            if child.type == "struct_declaration":
                return child

        return None

    def _parse_field(self, node: Node) -> dict | None:
        """Parse structure field node."""
        field_name = None
        field_type = None
        for child in node.children:
            if child.type == "identifier":
                field_name = self._get_node_text(child)
            elif child.type == ":":
                continue
            else:
                field_type = self._get_node_text(child)
                break

        if field_name and field_type:
            return {
                "name": field_name,
                "type": field_type,
                "doc": self._get_doc_comments(node),
            }

        return None


def _main() -> None:
    import json  # noqa: PLC0415

    code = """
    //! Module docs

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
