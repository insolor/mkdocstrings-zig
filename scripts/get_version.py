# Get current project version from Git tags or changelog.

import re
from contextlib import suppress
from pathlib import Path

from pdm.backend.hooks.version import SCMVersion, Version, default_version_formatter, get_version_from_scm

_root = Path(__file__).parent.parent
_default_scm_version = SCMVersion(Version("0.0.0"), None, False, None, None)  # noqa: FBT003


def get_version() -> str:
    scm_version = get_version_from_scm(_root) or _default_scm_version
    return default_version_formatter(scm_version)


if __name__ == "__main__":
    print(get_version())
