#!/usr/bin/env python
\"\"\"Clean cache and temporary files.\"\"\"
import shutil
from pathlib import Path
cache_dir = Path("data/cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("Cache cleaned.")