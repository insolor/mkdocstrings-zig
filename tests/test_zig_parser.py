from mkdocstrings_handlers.zig._internal.zig_docs_extractor import (
    _ZigDocsExtractor as ZigDocsExtractor,
)


def test_parser() -> None:
    zig_code = """
    //! This is module-level documentation
    //! It describes the entire file
    const std = @import("std");
    const AutoHashMap = std.AutoHashMap;

    /// Adds two numbers.
    fn add(a: i32, b: i32) i32 {
        return a  b;
    }

    /// A constant named PI.
    const PI = 3.14159;

    /// A 2D point struct.
    const Point = struct {
        /// horizontal coordinate
        x: i32,
        /// vertical coorinate
        y: i32,

        /// The top-left position
        pub const zero: Point = .{ .x = 0, .y = 0 };
    };

    /// Main function
    pub fn main() void {
        std.print("Hello, world!\n");
    }
    """

    parsed = ZigDocsExtractor(zig_code).get_docs()
    assert parsed == {
        "doc": "This is module-level documentation\nIt describes the entire file",
        "children": [
            {
                "node_type": "function",
                "doc": "Adds two numbers.",
                "name": "add",
                "signature": "fn add(a: i32, b: i32) i32",
            },
            {
                "node_type": "const",
                "doc": "A constant named PI.",
                "name": "PI",
            },
            {
                "node_type": "struct",
                "name": "Point",
                "doc": "A 2D point struct.",
                "children": [
                    {
                        "node_type": "fields",
                        "children": [
                            {
                                "doc": "horizontal coordinate",
                                "name": "x",
                                "type": "i32",
                            },
                            {
                                "doc": "vertical coorinate",
                                "name": "y",
                                "type": "i32",
                            },
                        ],
                    },
                    {
                        "node_type": "const",
                        "name": "zero",
                        "doc": "The top-left position",
                    },
                ],
            },
            {
                "node_type": "function",
                "name": "main",
                "doc": "Main function",
                "signature": "pub fn main() void",
            },
        ],
    }
