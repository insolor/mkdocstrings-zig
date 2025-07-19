from mkdocstrings_handlers.zig._internal.handler import ZigHandler


def test_parser():
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
    """

    parsed = ZigHandler._parse_zig_code(zig_code)
    assert parsed == {
        "module_docs": "This is module-level documentation\nIt describes the entire file",
        "functions": [{"name": "add", "doc": "Adds two numbers."}],
        "constants": [{"name": "PI", "doc": "A constant named PI."}],
        "structs": [{"name": "Point", "doc": "A 2D point struct."}],
    }
