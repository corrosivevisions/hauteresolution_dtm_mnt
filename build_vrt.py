#!/usr/bin/env python3
"""Builds a GDAL VRT from downloaded HRDEM tiles."""
from pathlib import Path
import subprocess
import sys


def main(base_dir: str = "HRDEM") -> None:
    tiles = [str(p) for p in Path(base_dir).rglob("*.tif")]
    if not tiles:
        print("No tiles found. Did you run download_hrdem.py?")
        return
    vrt_path = Path(base_dir) / "hrdem.vrt"
    subprocess.run(["gdalbuildvrt", str(vrt_path)] + tiles, check=True)
    print(f"VRT written to {vrt_path}")


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "HRDEM"
    main(base)
