import os
import json
import argparse
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import subprocess

BASE_URL = "https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/canada/hrdem-lidar/indexed/"

# Default directories and filenames
DEFAULT_OUTPUT_DIR = "HRDEM"
DEFAULT_PREVIEW_DIR = "previews"
DEFAULT_MANIFEST = "index_manifest.json"
DEFAULT_VRT = "hrdem.vrt"


def fetch_listing(url):
    """Return (subdirs, files) from an FTP-style HTML listing."""
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    subdirs, files = [], []
    for link in soup.find_all('a'):
        href = link.get('href')
        if not href or href.startswith('?') or href == '../':
            continue
        if href.endswith('/'):
            subdirs.append(href)
        else:
            files.append(href)
    return subdirs, files


def download_file(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        return dest
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return dest


def create_preview(tif_path, preview_path):
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    img = Image.open(tif_path)
    img = img.convert('L')
    img.save(preview_path)


def parse_info(relative_path):
    resolution = '1m' if '_1m_' in relative_path.lower() else '2m'
    zone = relative_path.split('/')[0] if '/' in relative_path else ''
    return {
        'file': relative_path,
        'zone': zone,
        'resolution': resolution
    }


def walk_and_download(base_url, rel_path, manifest, output_dir, preview_dir):
    subdirs, files = fetch_listing(base_url)
    for d in subdirs:
        walk_and_download(base_url + d, os.path.join(rel_path, d), manifest, output_dir, preview_dir)
    for f in files:
        if not f.endswith('.tif'):
            continue
        remote = base_url + f
        local = os.path.join(output_dir, rel_path, f)
        print(f"Downloading {remote}")
        download_file(remote, local)
        preview = os.path.join(preview_dir, rel_path, f.replace('.tif', '.png'))
        create_preview(local, preview)
        info = parse_info(os.path.join(rel_path, f))
        info['preview'] = preview
        manifest.append(info)


def build_vrt(tile_directory, vrt_file):
    try:
        subprocess.check_call([
            'gdalbuildvrt',
            '-input_file_list',
            '<(find {} -name "*.tif")'.format(tile_directory),
            vrt_file
        ], shell=True, executable='/bin/bash')
    except Exception:
        print('gdalbuildvrt not available. Skipping VRT creation.')


def main():
    parser = argparse.ArgumentParser(description="Download HRDEM tiles")
    parser.add_argument('--base-url', default=BASE_URL)
    parser.add_argument('--output', default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--previews', default=DEFAULT_PREVIEW_DIR)
    parser.add_argument('--manifest', default=DEFAULT_MANIFEST)
    parser.add_argument('--vrt', default=DEFAULT_VRT)
    args = parser.parse_args()

    output_dir = args.output
    preview_dir = args.previews
    manifest_file = args.manifest
    vrt_file = args.vrt

    manifest = []
    walk_and_download(args.base_url, '', manifest, output_dir, preview_dir)
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    build_vrt(output_dir, vrt_file)


if __name__ == '__main__':
    main()
