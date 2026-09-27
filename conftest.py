"""
Pytest conftest — add code dir to sys.path.
"""
import os
import sys

# Add v0.3-prelim/code to path so tests can import modules
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "v0.3-prelim", "code")
)
