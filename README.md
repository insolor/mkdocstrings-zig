# mkdocstrings-zig

[![ci](https://github.com/insolor/mkdocstrings-zig/workflows/ci/badge.svg)](https://github.com/insolor/mkdocstrings-zig/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://insolor.github.io/mkdocstrings-zig/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings-zig.svg)](https://pypi.org/project/mkdocstrings-zig/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocstrings-zig:gitter.im)

A Zig handler for mkdocstrings.

## Usage

### Installation

```bash
pip install mkdocstrings-zig
pip install mkdocs-material
```

`mkdocs-material` theme installation is optional, but recommended for better look and feel.

### mkdocs.yml example

```yaml
site_name: Example of zig project documentation using mkdocstrings

# remove if you are not using mkdocs-materail theme
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
