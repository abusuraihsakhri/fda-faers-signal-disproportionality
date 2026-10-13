#!/usr/bin/env python3
import os
import sys

# Use a fresh process-local key for CLI demos if no configured key is present.
# Deployed services must supply AUDIT_SECRET_KEY explicitly.
if not os.getenv("AUDIT_SECRET_KEY"):
    import secrets
    os.environ["AUDIT_SECRET_KEY"] = secrets.token_hex(32)

from faers_sentinel.cli import main

if __name__ == '__main__':
    sys.exit(main())
