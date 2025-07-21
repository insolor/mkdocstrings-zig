"""Zig handler for mkdocstrings."""

from mkdocstrings_handlers.zig._internal.config import (
    ZigConfig,
    ZigInputConfig,
    ZigInputOptions,
    ZigOptions,
)
from mkdocstrings_handlers.zig._internal.handler import ZigHandler, get_handler
from mkdocstrings_handlers.zig._internal.zig_docs_extractor import ZigDocsExtractor

__all__ = [
    "ZigConfig",
    "ZigDocsExtractor",
    "ZigHandler",
    "ZigInputConfig",
    "ZigInputOptions",
    "ZigOptions",
    "get_handler",
]
