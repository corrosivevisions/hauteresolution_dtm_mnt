# hauteresolution_dtm_mnt

This repository contains a script to download all available High-Resolution Digital Elevation Model (HRDEM) GeoTIFF tiles from Natural Resources Canada.

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`
- `Pillow`
- (optional) `gdal` for VRT creation

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python download_hrdem.py
```

By default all tiles are placed in the `HRDEM` directory and previews are written to `previews`. A JSON manifest named `index_manifest.json` is generated along with an optional VRT mosaic if GDAL is available.

Downloading the entire dataset is large (hundreds of gigabytes) and may take many hours depending on connection speed.

Run `python download_hrdem.py --help` for optional arguments to change directories or the base URL.
