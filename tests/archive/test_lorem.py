#!/usr/bin/env python3
"""
Quick test runner for lorem test framework
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from tests.run_lorem_test import main

if __name__ == "__main__":
    print("🧪 Running NAF Solution Wizard Lorem Test")
    main()
