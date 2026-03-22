"""Pytest configuration — ensure the backend package root is on sys.path."""
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
