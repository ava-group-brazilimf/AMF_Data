"""conftest.py — ensure 'scripts' package is importable from src/shared/scripts/."""
import sys
from pathlib import Path

# Add src/shared/ to sys.path so `from scripts.xxx import ...` works
_shared = Path(__file__).resolve().parent.parent
if str(_shared) not in sys.path:
    sys.path.insert(0, str(_shared))
