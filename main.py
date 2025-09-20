#!/usr/bin/env python3
"""
Wrapper script to run the Smart Code Review tool
"""
import sys
import os

# Add parent directory to path for local development
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run main function
from smart_code_review.main import main

if __name__ == "__main__":
    main()