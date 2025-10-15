"""scoopick package

Expose a small API and package version.
"""

import importlib.metadata

PACKAGE_NAME = "scoopick"

__version__ = importlib.metadata.version(PACKAGE_NAME)
