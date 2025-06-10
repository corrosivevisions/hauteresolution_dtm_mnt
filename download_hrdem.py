#!/usr/bin/env python3
"""Download HRDEM GeoTIFF tiles from NRCan.

This script recursively traverses the HRDEM FTP directory and downloads
all available .tif tiles, preserving the directory structure.
It also creates a JSON manifest file describing each tile.

Because the HRDEM FTP service is extremely large (~terabytes), the script
supports resuming interrupted downloads and will skip files that already
exist locally.

Usage:
    python download_hrdem.py [output_dir]

The output directory defaults to ``HRDEM`` in the current working
directory. Make sure ``gdalbuildvrt`` is available in your PATH if you
intend to build a VRT afterwards.
"""
from __future__ import annotations

import json
import os
from ftplib import FTP
from pathlib import Path
from typing import List, Dict

# FTP configuration
FTP_HOST = "ftp.maps.canada.ca"
FTP_BASE_PATH = "/pub/nrcan_rncan/elevation/canada/hrdem-lidar/indexed"

# Optional metadata CSV (contains tile bounding boxes, province, etc.)
METADATA_PATH = "/pub/nrcan_rncan/elevation/canada/hrdem-lidar/indexed/metadata/index.csv"


def connect() -> FTP:
    """Connect to the NRCan FTP server."""
    ftp = FTP(FTP_HOST)
    ftp.login()  # anonymous login
    return ftp


def list_dir(ftp: FTP, path: str) -> List[str]:
    """Return the directory listing for *path*."""
    entries: List[str] = []
    ftp.retrlines(f"NLST {path}", entries.append)
    return entries


def download_file(ftp: FTP, remote: str, local: Path) -> None:
    """Download a single file if it does not already exist."""
    if local.exists():
        return
    local.parent.mkdir(parents=True, exist_ok=True)
    with open(local, "wb") as fh:
        ftp.retrbinary(f"RETR {remote}", fh.write)


def walk_and_download(ftp: FTP, remote_dir: str, local_base: Path, manifest: List[Dict[str, str]]):
    """Recursively download all .tif files from *remote_dir*."""
    for entry in list_dir(ftp, remote_dir):
        # Determine if entry is a directory or file by trying to CWD into it
        full_remote = f"{remote_dir}/{entry}".replace("//", "/")
        try:
            ftp.cwd(full_remote)
            ftp.cwd("..")
            # It's a directory
            walk_and_download(ftp, full_remote, local_base, manifest)
        except Exception:
            # Not a directory, assume file
            if entry.lower().endswith(".tif"):
                local_path = local_base / os.path.relpath(full_remote, FTP_BASE_PATH)
                download_file(ftp, full_remote, local_path)
                manifest.append({"file": str(local_path), "remote": full_remote})


def load_metadata(ftp: FTP) -> Dict[str, Dict[str, str]]:
    """Load the optional metadata CSV if available."""
    meta: Dict[str, Dict[str, str]] = {}
    try:
        lines: List[str] = []
        ftp.retrlines(f"RETR {METADATA_PATH}", lines.append)
        # Expect CSV with columns like file,province,utm_zone,lat_min,lat_max,lon_min,lon_max,resolution
        import csv
        reader = csv.DictReader(lines)
        for row in reader:
            meta[row["file"]] = row
    except Exception:
        # metadata not available
        pass
    return meta


def main(output_dir: str = "HRDEM") -> None:
    ftp = connect()
    metadata = load_metadata(ftp)
    manifest: List[Dict[str, str]] = []
    walk_and_download(ftp, FTP_BASE_PATH, Path(output_dir), manifest)
    # merge metadata if available
    for item in manifest:
        file_key = os.path.basename(item["file"])
        if file_key in metadata:
            item.update(metadata[file_key])
    with open(Path(output_dir) / "index_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    ftp.quit()


if __name__ == "__main__":
    import sys

    out_dir = sys.argv[1] if len(sys.argv) > 1 else "HRDEM"
    main(out_dir)
