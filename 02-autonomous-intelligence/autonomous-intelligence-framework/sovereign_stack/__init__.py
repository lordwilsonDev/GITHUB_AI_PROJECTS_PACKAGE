import os, sys
_here = os.path.dirname(__file__)
target = os.path.abspath(os.path.join(_here, "..", "sovereign-stack"))
if target not in sys.path:
    sys.path.insert(0, target)
