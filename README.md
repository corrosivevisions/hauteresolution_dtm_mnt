# hauteresolution_dtm_mnt

Helper script for mirroring Natural Resources Canada's High-Resolution Digital Elevation Model (HRDEM) tiles.

## Usage

```bash
python3 download_hrdem.py /path/to/output \
    --manifest index_manifest.json \
    --vrt hrdem.vrt
```

The script connects to NRCan's public FTP service and recursively downloads all
`*.tif` tiles while preserving the UTM directory layout. After downloading, a
JSON manifest with basic metadata is written and a GDAL VRT mosaic is created.
Preview PNGs are generated if `gdal_translate` is found on your system.

Downloading the entire HRDEM archive requires substantial disk space and may
take many hours.
