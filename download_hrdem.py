import os
import json
import argparse
from ftplib import FTP
from pathlib import Path
import rasterio
import subprocess
from typing import List, Dict

# Optional preview generation requires GDAL utilities
PREVIEW_SUFFIX = "_preview.png"

FTP_HOST = "ftp.maps.canada.ca"
FTP_BASE = "/pub/nrcan_rncan/elevation/canada/hrdem-lidar/indexed"

def list_dir(ftp: FTP, path: str):
    """List entries in a directory using MLSD when available."""
    try:
        return list(ftp.mlsd(path))
    except Exception:
        ftp.cwd(path)
        entries = []
        ftp.retrlines('LIST', lambda line: entries.append(line))
        result = []
        for e in entries:
            parts = e.split(None, 8)
            name = parts[-1]
            entry_type = 'dir' if e.startswith('d') else 'file'
            result.append((name, {'type': entry_type}))
        ftp.cwd('..')
        return result

def download_file(ftp: FTP, remote_file: str, local_file: Path):
    local_file.parent.mkdir(parents=True, exist_ok=True)
    with open(local_file, 'wb') as f:
        ftp.retrbinary(f"RETR {remote_file}", f.write)

def generate_preview(tif_path: Path):
    png_path = tif_path.with_suffix('')
    png_path = png_path.parent / (png_path.name + PREVIEW_SUFFIX)
    subprocess.run([
        'gdal_translate',
        '-of', 'PNG',
        '-scale',
        str(tif_path),
        str(png_path)
    ], check=False)
    return str(png_path)

def extract_metadata(path: Path) -> Dict:
    with rasterio.open(path) as ds:
        bbox = list(ds.bounds)
        res = ds.res[0]
    return {
        'filename': str(path),
        'bbox': bbox,
        'resolution': res
    }

def traverse_and_download(ftp: FTP, remote_dir: str, local_dir: Path, manifest: List[Dict]):
    for name, facts in list_dir(ftp, remote_dir):
        remote_path = f"{remote_dir}/{name}"
        if facts.get('type') == 'dir':
            traverse_and_download(ftp, remote_path, local_dir / name, manifest)
        elif name.lower().endswith('.tif'):
            local_file = local_dir / name
            print(f"Downloading {remote_path}")
            download_file(ftp, remote_path, local_file)
            preview = generate_preview(local_file)
            info = extract_metadata(local_file)
            info['preview'] = preview
            manifest.append(info)

def generate_vrt(vrt_path: Path, tiles_dir: Path):
    print("Generating VRT ...")
    tile_list = [str(p) for p in tiles_dir.rglob('*.tif')]
    if not tile_list:
        print("No tiles found to build VRT")
        return
    subprocess.run(['gdalbuildvrt', str(vrt_path)] + tile_list, check=False)

def main():
    parser = argparse.ArgumentParser(description="Download HRDEM tiles")
    parser.add_argument('dest', help="Destination directory")
    parser.add_argument('--manifest', default='index_manifest.json', help="Manifest file")
    parser.add_argument('--vrt', default='hrdem.vrt', help="Output VRT file")
    args = parser.parse_args()
    dest = Path(args.dest)
    manifest_data = []
    with FTP(FTP_HOST) as ftp:
        ftp.login()
        traverse_and_download(ftp, FTP_BASE, dest, manifest_data)
    with open(args.manifest, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    generate_vrt(Path(args.vrt), dest)

if __name__ == '__main__':
    main()
