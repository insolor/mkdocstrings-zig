# mkdocstrings-zig

A Zig handler for [mkdocstrings](https://mkdocstrings.github.io). Makes it possible to create documentation from code in Zig language using [mkdocs](https://github.com/mkdocs/mkdocs).

## Demo

See [demo documentation](https://insolor.github.io/mkdocstrings-zig/demo) generated from [test_zig_project](https://github.com/insolor/mkdocstrings-zig/tree/main/test_zig_project).

## Usage

### Installation

```
pip install 'mkdocstrings[zig]'
pip install mkdocs-material
pip install typing-extensions

```

Technically, it can work without [mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme, but it doesn't generate table of contents without the theme.

### mkdocs.yml example

```
site_name: Example of zig project documentation using mkdocstrings

# remove if you are not using mkdocs-material theme
# or replace it with the theme of your choice
theme:
  name: material

plugins:
- mkdocstrings:
    default_handler: zig

```

### docs/index.md example

```
# Project Documentation

::: src/main.zig

::: src/root.zig

```

Or add documentation for a directory:

```
::: src

```
