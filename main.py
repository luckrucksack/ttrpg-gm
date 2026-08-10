#!/usr/bin/env python3
"""Entry shim for the AI-GM runtime.

Kept at repo root for backward compatibility with launchers and docs.
The actual implementation lives in gm_core/runtime.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gm_core.runtime import main

if __name__ == "__main__":
    main()
