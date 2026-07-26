#!/usr/bin/env python3
"""
RED Core Root Entry Point Wrapper.
Imports and launches the core RED execution loop from core/red.py.
"""
import os
import sys
import io
import logging

# Ensure Windows stdio handles all unicode characters safely without cp1252 exceptions
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure logging handlers don't crash on unencodable characters
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
for h in logging.root.handlers:
    if hasattr(h, 'setStream') or isinstance(h, logging.StreamHandler):
        h.setLevel(logging.INFO)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.red import red_loop

if __name__ == "__main__":
    red_loop()
