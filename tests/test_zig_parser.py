from mkdocstrings_handlers.zig._internal.handler import ZigHandler


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
        x: i32,
        y: i32,
    };

    /// Main function
    pub fn main() void {
        std.print("Hello, world!\n");
    }
    """

    parsed = ZigHandler._parse_zig_code(zig_code)
    assert parsed == {
        "docstring": "This is module-level documentation\nIt describes the entire file",
        "functions": [
            {
                "name": "add",
                "docstring": "Adds two numbers.",
                "signature": "fn add(a: i32, b: i32) i32",
            },
            {"name": "main", "docstring": "Main function", "signature": "pub fn main() void"},
        ],
        "constants": [
            {
                "name": "PI",
                "signature": "const PI = 3.14159;",
                "docstring": "A constant named PI.",
            },
        ],
        "structs": [
            {
                "name": "Point",
                "signature": None,
                "docstring": "A 2D point struct.",
            },
        ],
    }
