import os
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/canada/hrdem-lidar/indexed/"

MANIFEST_FILE = "index_manifest.json"
DATA_DIR = "HRDEM"
VRT_FILE = "hrdem.vrt"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def list_links(url):
    """Return href links from an index page"""
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and href not in ("../", "/"):
            yield href


def download_file(url, out_path):
    print(f"Downloading {url} -> {out_path}")
    ensure_dir(os.path.dirname(out_path))
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def traverse(base_url, local_dir, manifest):
    for link in list_links(base_url):
        if link.endswith('/'):
            traverse(urljoin(base_url, link), os.path.join(local_dir, link), manifest)
        elif link.lower().endswith('.tif'):
            dest = os.path.join(local_dir, link)
            url = urljoin(base_url, link)
            download_file(url, dest)
            meta = get_metadata(dest)
            manifest.append(meta)


def get_metadata(tif_path):
    try:
        import rasterio
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            res = max(src.res)
            crs = src.crs.to_string()
    except Exception as e:
        bounds = None
        res = None
        crs = None
    return {
        "file": tif_path,
        "bounds": bounds and list(bounds),
        "crs": crs,
        "resolution": res,
    }


def write_manifest(manifest):
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)


def build_vrt():
    os.system(f"gdalbuildvrt -input_file_list <(find {DATA_DIR} -name '*.tif') {VRT_FILE}")


if __name__ == "__main__":
    manifest = []
    traverse(BASE_URL, DATA_DIR, manifest)
    write_manifest(manifest)
    build_vrt()
