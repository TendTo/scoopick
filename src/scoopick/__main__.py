"""Module to support `python -m scoopick`."""

import sys
from .app import main


if __name__ == "__main__":
    sys.exit(main())
