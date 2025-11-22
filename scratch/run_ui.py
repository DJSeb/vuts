#!/usr/bin/env python3
"""
Quick launcher script for VUTS Web UI.

This script provides an easy way to start the web interface.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the app
from ui.app import main

if __name__ == '__main__':
    main()
