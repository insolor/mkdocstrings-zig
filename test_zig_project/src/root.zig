//! By convention, **root.zig** is the root source file when making a library. If
//! you are making an executable, the convention is to delete this file and
//! start with **main.zig** instead.
const std = @import("std");
const testing = std.testing;

/// Example `add` function
pub export fn add(a: i32, b: i32) i32 {
    return a + b;
}

test "basic add functionality" {
    try testing.expect(add(3, 7) == 10);
}

/// Point structure
const Point = struct {
    /// Horizontal coordinate
    x: u32,
    /// Vertical coordinate
    y: u32,

    /// Some function
    pub fn someFunc(a: i32) void {
        _ = a;
    }
};

/// 3d vector structure
const Vec3 = struct { x: f32, y: f32, z: f32 };
