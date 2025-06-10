# hauteresolution_dtm_mnt

Downloads all available High-Resolution Digital Elevation Model (HRDEM) GeoTIFF tiles for the entire country of Canada from Natural Resources Canada's FTP or HTTPS endpoint.

## Usage

```
python download_hrdem.py [--out-dir PATH] [--url-base URL] [--ftp]
```

- `--out-dir` specifies where the files will be stored. The default is `./data`.
- `--url-base` changes the base URL to download from. The default is `https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/dtm_mnt/2m/`.
- `--ftp` switches to the FTP protocol for servers that require it.

Files are saved replicating the directory structure from the remote server. Downloads can be resumed and will retry on failures.
