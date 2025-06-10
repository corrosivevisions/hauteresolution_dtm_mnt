# hauteresolution_dtm_mnt

This repository contains helper scripts to download the High-Resolution
Digital Elevation Model (HRDEM) tiles from Natural Resources Canada.
The dataset is extremely large (multiple terabytes). The scripts do not
bundle the data themselves; instead they automate fetching the tiles and
building a manifest once run in an environment with network access to the
NRCan FTP service.

## Scripts

* `download_hrdem.py` – recursively downloads all `.tif` tiles and writes
  `index_manifest.json` with basic metadata.
* `build_vrt.py` – builds a single GDAL VRT (`hrdem.vrt`) from the
  downloaded tiles for easy import into QGIS or Blender.
* `generate_previews.py` – optional tool to create grayscale PNG previews
  for each tile using `gdal_translate`.

## Usage

```
python download_hrdem.py HRDEM
python build_vrt.py HRDEM
python generate_previews.py HRDEM  # optional
```

The resulting `HRDEM` folder can be imported directly into QGIS. The
`hrdem.vrt` file references every downloaded tile for quick viewing and
analysis. Use the PNG previews for rapid visual sorting or terrain
selection.
