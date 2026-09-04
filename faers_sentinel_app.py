#!/usr/bin/env python3
import os
import sys

# Ensure AUDIT_SECRET_KEY is set
if not os.getenv("AUDIT_SECRET_KEY"):
    os.environ["AUDIT_SECRET_KEY"] = "faers-sentinel-dev-key-change-in-production-2026"

from faers_sentinel.cli import main

if __name__ == '__main__':
    sys.exit(main())
