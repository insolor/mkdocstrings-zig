from mkdocstrings_handlers.zig._internal.zig_docs_extractor import (
    _ZigDocsExtractor as ZigDocsExtractor,
)


def test_parser() -> None:
    zig_code = """
    //! This is module-level documentation
    //! It describes the entire file

    /// Adds two numbers.
    fn add(a: i32, b: i32) i32 {
        return a + b;
    }

    /// A constant named PI.
    const PI = 3.14159;

    /// A 2D point struct.
    const Point = struct {
        /// horizontal coordinate
        x: i32,
        /// vertical coorinate
        y: i32,
    };

    /// Main function
    pub fn main() void {
        std.print("Hello, world!\n");
    }
    """

    parsed = ZigDocsExtractor(zig_code).get_docs()
    assert parsed == {
        "doc": "This is module-level documentation\nIt describes the entire file",
        "functions": [
            {
                "name": "add",
                "doc": "Adds two numbers.",
                "signature": "fn add(a: i32, b: i32) i32",
            },
            {
                "name": "main",
                "doc": "Main function",
                "signature": "pub fn main() void",
            },
        ],
        "constants": [
            {
                "name": "PI",
                "doc": "A constant named PI.",
            },
        ],
        "structs": [
            {
                "name": "Point",
                "doc": "A 2D point struct.",
                "fields": [
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
        ],
    }
