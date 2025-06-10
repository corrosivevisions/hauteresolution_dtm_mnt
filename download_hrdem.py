import argparse
import os
import re
import sys
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
try:
    from ftplib import FTP
except ImportError:
    FTP = None


LISTING_RE = re.compile(r'href="([^"]+)"')


def parse_args():
    p = argparse.ArgumentParser(description="Download HRDEM GeoTIFF tiles")
    p.add_argument('--out-dir', default='data', help='Directory to store downloads')
    p.add_argument('--url-base', default='https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/dtm_mnt/2m/', help='Base URL to download from')
    p.add_argument('--ftp', action='store_true', help='Use FTP protocol instead of HTTP')
    p.add_argument('--retries', type=int, default=3, help='Retry attempts for failed downloads')
    return p.parse_args()


def ensure_session(retries):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def list_http(session, url):
    r = session.get(url)
    r.raise_for_status()
    paths = LISTING_RE.findall(r.text)
    # Filter out parent directory links
    return [p for p in paths if p and not p.startswith('?')]


def download_http(session, url, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    temp_path = local_path + '.part'
    resume_header = {}
    if os.path.exists(temp_path):
        resume_header['Range'] = f'bytes={os.path.getsize(temp_path)}-'
        mode = 'ab'
    else:
        mode = 'wb'
    with session.get(url, stream=True, headers=resume_header) as r:
        r.raise_for_status()
        with open(temp_path, mode) as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    os.rename(temp_path, local_path)


def list_ftp(ftp, path):
    entries = []
    ftp.retrlines(f'LIST {path}', lambda line: entries.append(line))
    files = []
    dirs = []
    for entry in entries:
        parts = entry.split()
        name = parts[-1]
        if entry.lower().startswith('d'):
            dirs.append(name)
        else:
            files.append(name)
    return files, dirs


def download_ftp(ftp, remote_path, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    temp_path = local_path + '.part'
    resume_size = 0
    if os.path.exists(temp_path):
        resume_size = os.path.getsize(temp_path)
    mode = 'ab' if resume_size else 'wb'
    with open(temp_path, mode) as f:
        if resume_size:
            ftp.retrbinary(f'REST {resume_size}', lambda data: None)
        ftp.retrbinary(f'RETR {remote_path}', f.write, rest=resume_size)
    os.rename(temp_path, local_path)


def recursive_download_http(session, base_url, rel_path, out_dir):
    url = urljoin(base_url, rel_path)
    items = list_http(session, url)
    for item in items:
        if item.endswith('/'):
            recursive_download_http(session, base_url, os.path.join(rel_path, item), out_dir)
        else:
            local_path = os.path.join(out_dir, rel_path, item)
            download_http(session, urljoin(url, item), local_path)


def recursive_download_ftp(ftp, base_path, rel_path, out_dir):
    path = os.path.join(base_path, rel_path)
    files, dirs = list_ftp(ftp, path)
    for f in files:
        local_path = os.path.join(out_dir, rel_path, f)
        download_ftp(ftp, os.path.join(path, f), local_path)
    for d in dirs:
        recursive_download_ftp(ftp, base_path, os.path.join(rel_path, d), out_dir)


def main():
    args = parse_args()
    out_dir = args.out_dir
    if args.ftp:
        if FTP is None:
            print('FTP support is not available in this environment', file=sys.stderr)
            return 1
        url = urlparse(args.url_base)
        ftp = FTP(url.hostname)
        ftp.login()
        base_path = url.path
        recursive_download_ftp(ftp, base_path, '', out_dir)
        ftp.quit()
    else:
        session = ensure_session(args.retries)
        recursive_download_http(session, args.url_base, '', out_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
