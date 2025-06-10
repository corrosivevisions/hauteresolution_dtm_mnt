# hauteresolution_dtm_mnt

Downloads all available High-Resolution Digital Elevation Model (HRDEM) GeoTIFF tiles for the entire country of Canada from Natural Resources Canada’s FTP or HTTPS endpoint.

## Prerequisites

- Python 3.8 or higher
- `pip` for installing Python packages

Install the required packages with:

```bash
pip install -r requirements.txt
```

## Usage

Run the download script to fetch HRDEM data. Example:

```bash
python download_hrdem.py --output ./data
```

The script downloads every available tile and places them under the folder specified by `--output`.

## Dataset

The [High-Resolution Digital Elevation Model (HRDEM)](https://open.canada.ca/data/en/dataset/14f46e24-1f51-4fb9-8bcd-7ccfa86a7b71) is produced by Natural Resources Canada (NRCan) as part of the National Elevation Data Strategy. It provides detailed elevation information at 1 m or better resolution. Additional information can be found on [NRCan’s topographic data page](https://www.nrcan.gc.ca/maps-tools-and-publications/maps/topographic-information/data/1275).

## Expected output

After running the script, your directory might look like:

```
data/
├── NTS_031L04/
│   ├── hrdem-dtm-031L04_0200_0200.tif
│   └── ...
├── NTS_031L05/
│   └── hrdem-dtm-031L05_0200_0200.tif
└── ...
```

Each subfolder corresponds to a National Topographic System (NTS) tile containing one or more GeoTIFF files.
