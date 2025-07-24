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
        children = []

        for child in node.children:
            if child.type == "comment":
                text = self._get_node_text(child)
                if text.startswith("//!"):
                    module_doc.append(text[3:].strip())
            if child.type == "container_field":
                field = self._parse_field(child)
                if field:
                    if not fields:
                        children.append(
                            {
                                "node_type": "fields",
                                "children": fields,
                            },
                        )

                    fields.append(field)
            elif child.type == "function_declaration":
                function = self._parse_function(child)
                if function:
                    children.append(function)
            elif child.type == "variable_declaration":
                if self._is_import(child):
                    continue

                name = self._get_node_name(child)
                if not name:
                    continue

                doc = self._get_doc_comments(child)
                struct_node = self._get_struct_declaration(child)
                if struct_node:
                    children.append(
                        {
                            "node_type": "struct",
                            "short_signature": self._get_short_struct_signature(child),
                            "name": name,
                            "doc": doc,
                            **self._parse_structure(struct_node),
                        },
                    )
                elif doc:
                    children.append(
                        {
                            "node_type": "const",
                            "short_signature": self._get_short_const_signature(child),
                            "name": name,
                            "doc": doc,
                        },
                    )

        result = {}
        if module_doc:
            result["doc"] = "\n".join(module_doc)

        if children:
            result["children"] = children

        return result

    def _parse_function(self, node: Node) -> dict | None:
        """Parse function information."""
        fn_name = self._get_node_name(node)
        doc_comment = self._get_doc_comments(node)
        if fn_name and doc_comment:
            result = {
                "node_type": "function",
                "name": fn_name,
                "doc": doc_comment,
                "signature": self._get_function_signature(node),
                "short_signature": self._get_short_function_signature(node),
            }

            return_struct = self._get_return_struct(node)
            if return_struct:
                result["return_struct"] = return_struct

            return result

        return None

    def _get_function_signature(self, node: Node) -> str:
        """Extract signature of the function."""
        return self._get_node_text(node).split("{")[0].strip()

    def _get_short_function_signature(self, node: Node) -> str:
        """Extract short function signature."""
        return self._get_node_text(node).split("(")[0].strip()

    def _get_node_name(self, node: Node) -> str | None:
        """Get node identifier as it's name."""
        for child in node.children:
            if child.type in ("identifier", "builtin_identifier"):
                return self._get_node_text(child)

        return None

    def _is_import(self, node: Node) -> bool:
        """Check if the given constant is an import."""
        for child in node.children:
            if (
                child.type == "builtin_function"
                and self._get_node_name(child) == "@import"
            ):
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

    def _get_short_const_signature(self, node: Node) -> str:
        """Use everything before = in the const declaration as a short signature"""
        return self._get_node_text(node).split("=")[0].strip()

    def _get_short_struct_signature(self, node: Node) -> str:
        """
        Get short const signature and replace `cosnt` with `struct`,
        so `pub const Point` will be `pub struct Point`.
        """
        return "struct".join(self._get_short_const_signature(node).split("const"))

    def _parse_field(self, node: Node) -> dict | None:
        """Parse structure field node."""
        field_name = None
        field_type = None
        for child in node.children:
            if child.type == "identifier" and not field_name:
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

    def _get_return_struct(self, node: Node) -> dict | None:
        """
        Parse structure returned from a function.
        Probably recursive search for return is needed, but for we support only basic case.
        """
        function_body = self._get_function_body(node)
        if not function_body:
            return None

        for child in function_body.children:
            if child.type == "expression_statement":
                return_expression = self._get_return_expression(child)
                if not return_expression:
                    continue

                struct = self._get_struct_declaration(return_expression)
                if not struct:
                    continue

                parsed_struct = self._parse_structure(struct)
                if not parsed_struct:
                    continue

                parsed_struct["node_type"] = "struct"
                return parsed_struct

        return None

    def _get_function_body(self, node: Node) -> Node | None:
        """Get the block which represents the function's body"""
        for child in node.children:
            if child.type == "block":
                return child

        return None

    def _get_return_expression(self, node: Node) -> Node | None:
        """Check if the statement is return and return the return value"""
        for child in node.children:
            if child.type == "return_expression":
                return child

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

    /// Generic structure factory example
    fn GenericStructure(comptime T: type) type {
        return struct {
            /// Contained value
            value: T,
        };
    }
    """

    extractor = _ZigDocsExtractor(code)
    print(json.dumps(extractor.get_docs(), indent=4))  # noqa: T201


if __name__ == "__main__":
    _main()
