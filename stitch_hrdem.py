# -*- coding: utf-8 -*-
"""Stitch HRDEM tiles into a single national DEM.

This script scans a directory for HRDEM GeoTIFF tiles, ensures they are in
EPSG:4326, builds a VRT and finally outputs a single compressed GeoTIFF.
It is designed to handle large datasets by streaming data via GDAL.
"""

import os
import argparse
import logging

from osgeo import gdal, osr


def find_tiles(base_dir):
    """Recursively collect all .tif files under base_dir."""
    tile_paths = []
    for root, _, files in os.walk(base_dir):
        for name in files:
            if name.lower().endswith('.tif'):
                tile_paths.append(os.path.join(root, name))
    return tile_paths


def is_epsg4326(dataset):
    """Return True if the dataset's CRS is EPSG:4326."""
    wkt = dataset.GetProjection()
    if not wkt:
        return False
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    authority = srs.GetAuthorityCode(None)
    return authority == '4326'


def reproject_to_4326(src_path):
    """Reproject a raster to EPSG:4326 if necessary.

    Returns the path to the (potentially reprojected) file and a bool
    indicating whether reprojection occurred.
    """
    ds = gdal.Open(src_path)
    if ds is None:
        raise RuntimeError(f"Failed to open {src_path}")

    if is_epsg4326(ds):
        ds = None
        return src_path, False

    dst_path = os.path.splitext(src_path)[0] + "_4326.tif"
    logging.info("Reprojecting %s -> %s", src_path, dst_path)

    gdal.Warp(
        dst_path,
        ds,
        dstSRS='EPSG:4326',
        format='GTiff',
        creationOptions=['TILED=YES', 'COMPRESS=LZW'],
        warpOptions=['NUM_THREADS=ALL_CPUS']
    )
    ds = None
    return dst_path, True


def build_vrt(vrt_path, tile_list):
    """Build a GDAL VRT from the list of tile paths."""
    logging.info("Building VRT %s", vrt_path)
    vrt = gdal.BuildVRT(vrt_path, tile_list)
    if vrt is None:
        raise RuntimeError("VRT creation failed")
    vrt = None


def translate_vrt_to_gtiff(vrt_path, output_path):
    """Translate VRT to a compressed GeoTIFF with nodata handling."""
    logging.info("Translating VRT to final GeoTIFF %s", output_path)
    gdal.Translate(
        output_path,
        vrt_path,
        format='GTiff',
        creationOptions=['TILED=YES', 'COMPRESS=LZW'],
    )


def log_output_info(output_path):
    """Log file size and bounds of the output GeoTIFF."""
    ds = gdal.Open(output_path)
    if ds is None:
        logging.error("Failed to open output DEM")
        return

    gt = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    xmin = gt[0]
    ymax = gt[3]
    xmax = gt[0] + gt[1] * cols
    ymin = gt[3] + gt[5] * rows
    ds = None

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logging.info("Output size: %.2f MB", size_mb)
    logging.info("Output bounds: [%.4f, %.4f, %.4f, %.4f]", xmin, ymin, xmax, ymax)


def main():
    parser = argparse.ArgumentParser(description="Stitch HRDEM tiles into a single DEM")
    parser.add_argument('--input-dir', required=True, help="Base directory of tiles")
    parser.add_argument('--output', required=True, help="Path to final GeoTIFF")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    gdal.SetConfigOption('GDAL_CACHEMAX', '512')

    tiles = find_tiles(args.input_dir)
    logging.info("%d tiles found", len(tiles))
    if not tiles:
        logging.error("No tiles discovered. Exiting.")
        return

    processed_tiles = []
    for path in tiles:
        try:
            new_path, reprojected = reproject_to_4326(path)
            if reprojected:
                logging.info("Reprojected tile %s", os.path.basename(path))
            processed_tiles.append(new_path)
        except Exception as err:
            logging.error("%s", err)

    vrt_path = os.path.join(os.path.dirname(args.output), 'temp_mosaic.vrt')
    build_vrt(vrt_path, processed_tiles)

    translate_vrt_to_gtiff(vrt_path, args.output)
    log_output_info(args.output)


if __name__ == '__main__':
    main()
