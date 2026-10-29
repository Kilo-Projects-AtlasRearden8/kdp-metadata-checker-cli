"""Allow running the package as `python -m kdp_metadata_checker`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
