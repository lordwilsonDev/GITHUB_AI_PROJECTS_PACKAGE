import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
if MODULES.exists():
    sys.path.insert(0, str(MODULES))
sys.path.insert(0, str(ROOT))
