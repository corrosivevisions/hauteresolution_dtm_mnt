#!/usr/bin/env python3
"""Generate grayscale PNG previews for each HRDEM tile."""
from pathlib import Path
import subprocess
import sys


def convert_tile(tif_path: Path, png_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "gdal_translate",
        "-ot", "Byte",
        "-of", "PNG",
        "-scale", "0", "65535", "0", "255",
        str(tif_path),
        str(png_path),
    ], check=True)


def main(base_dir: str = "HRDEM") -> None:
    for tif in Path(base_dir).rglob("*.tif"):
        png = tif.with_suffix(".png")
        if png.exists():
            continue
        convert_tile(tif, png)
        print(f"Preview created: {png}")


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "HRDEM"
    main(base)
