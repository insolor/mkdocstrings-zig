# This module implements a handler for Zig.

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import markdown
from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectorItem, get_logger

from mkdocstrings_handlers.zig._internal.config import ZigConfig, ZigOptions
from mkdocstrings_handlers.zig._internal.zig_docs_extractor import _ZigDocsExtractor as ZigDocsExtractor

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocstrings import HandlerOptions


_logger = get_logger(__name__)


class ZigHandler(BaseHandler):
    """The Zig handler class."""

    name: ClassVar[str] = "zig"
    """The handler's name."""

    domain: ClassVar[str] = "zig"
    """The cross-documentation domain/language for this handler."""
    # Typically: the file extension, like `py`, `go` or `rs`.
    # For non-language handlers, use the technology/tool name, like `openapi` or `click`.

    enable_inventory: ClassVar[bool] = False
    """Whether this handler is interested in enabling the creation of the `objects.inv` Sphinx inventory file."""

    fallback_theme: ClassVar[str] = "material"
    """The theme to fallback to."""

    def __init__(self, config: ZigConfig, base_dir: Path, **kwargs: Any) -> None:
        """Initialize the handler.

        Parameters:
            config: The handler configuration.
            base_dir: The base directory of the project.
            **kwargs: Arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.config = config
        """The handler configuration."""
        self.base_dir = base_dir
        """The base directory of the project."""
        self.global_options = config.options
        """The global configuration options."""

        self._collected: dict[str, CollectorItem] = {}

    def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
        """Get combined default, global and local options.

        Arguments:
            local_options: The local options.

        Returns:
            The combined options.
        """
        extra = {
            **self.global_options.get("extra", {}),
            **local_options.get("extra", {}),
        }
        options = {**self.global_options, **local_options, "extra": extra}
        try:
            return ZigOptions.from_data(**options)
        except Exception as error:
            raise PluginError(f"Invalid options: {error}") from error

    def collect(self, identifier: str, options: ZigOptions) -> CollectorItem:  # noqa: ARG002
        """Collect data given an identifier and selection configuration."""
        # If identifier is a file path
        if identifier.endswith(".zig"):
            with open(identifier, encoding="utf-8") as f:
                code = f.read()
        else:  # Treat as raw code
            code = identifier

        # Parse Zig code
        parsed = ZigDocsExtractor(code).get_docs()

        parsed["path"] = identifier
        parsed["name"] = identifier
        return parsed

    def render(self, data: CollectorItem, options: ZigOptions) -> str:
        """Render a template using provided data and configuration options."""
        # The `data` argument is the data to render, that was collected above in `collect()`.
        # The `options` argument is the configuration options for loading/rendering the data.
        # It contains both the global and local options, combined together.

        # You might want to get the template based on the data type.
        template = self.env.get_template("data.html.jinja")
        # All the following variables will be available in the Jinja templates.
        return template.render(
            config=options,
            data=data,  # You might want to rename `data` into something more specific.
            heading_level=options.heading_level,
            root=True,
        )

    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Get aliases for a given identifier."""
        try:
            data = self._collected[identifier]
        except KeyError:
            return ()
        # Update the following code to return the canonical identifier and any aliases.
        return (data.path,)

    def update_env(self, config: dict) -> None:  # noqa: ARG002
        """Update the Jinja environment with any custom settings/filters/options for this handler.

        Parameters:
            config: MkDocs configuration, read from `mkdocs.yml`.
        """
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["markdown"] = markdown.markdown

    # You can also implement the `get_inventory_urls` and `load_inventory` methods
    # if you want to support loading object inventories.
    # You can also implement the `render_backlinks` method if you want to support backlinks.


def get_handler(
    handler_config: MutableMapping[str, Any],
    tool_config: MkDocsConfig,
    **kwargs: Any,
) -> ZigHandler:
    """Simply return an instance of `ZigHandler`.

    Arguments:
        handler_config: The handler configuration.
        tool_config: The tool (SSG) configuration.

    Returns:
        An instance of `ZigHandler`.
    """
    base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
    return ZigHandler(
        config=ZigConfig.from_data(**handler_config),
        base_dir=base_dir,
        **kwargs,
    )
