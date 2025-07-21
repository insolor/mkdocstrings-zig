# mkdocstrings-zig

[![ci](https://github.com/insolor/mkdocstrings-zig/workflows/ci/badge.svg)](https://github.com/insolor/mkdocstrings-zig/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://insolor.github.io/mkdocstrings-zig/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings-zig.svg)](https://pypi.org/project/mkdocstrings-zig/)

A Zig handler for [mkdocstrings](https://mkdocstrings.github.io). Makes it possible to create documentation from code in Zig language using [mkdocs](https://github.com/mkdocs/mkdocs).

## Demo

See [demo documentation](https://insolor.github.io/mkdocstrings-zig/demo) generated from [test_zig_project](https://github.com/insolor/mkdocstrings-zig/tree/main/test_zig_project).

## Usage

### Installation

```bash
pip install 'mkdocstrings[zig]'
pip install mkdocs-material
pip install typing-extensions
```

[mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme installation is optional, but recommended for better look and feel.

### mkdocs.yml example

```yaml
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

```markdown
# Project Documentation

::: src/main.zig

::: src/root.zig
```

In the future it's planned to add a possibility to specify just a parent directory, like that:

```markdown
::: src
```
