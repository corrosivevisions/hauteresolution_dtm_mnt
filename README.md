# hauteresolution_dtm_mnt

This repository contains a small utility script for **mirroring** the HRDEM
(High-Resolution Digital Elevation Model) tiles from the Natural Resources
Canada open data site. The dataset is extremely large and cannot be shipped with
this repository.

## Usage

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the downloader (this will fetch many GBs of data):
   ```bash
   python download_hrdem.py
   ```
   The script recreates the remote directory structure inside the `HRDEM/`
   folder, generates `index_manifest.json` with basic metadata for each tile and
   builds `hrdem.vrt` for easy use in GIS software.

The script relies on `requests`, `beautifulsoup4`, `rasterio` and `gdal`
(`gdalbuildvrt` must be available in your PATH). Network issues or large data
volumes may require additional configuration.
