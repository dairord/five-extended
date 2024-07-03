from datetime import datetime
import os
import rasterio
from rasterio.transform import from_bounds, Affine
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import box
import numpy as np
from pathlib import Path

global name, lat1, lon1, lat2, lon2
base_dir = Path(__file__).parent.parent

def generate_tif(image_path, lat1, lon1, lat2, lon2):
    with rasterio.open(image_path) as src:
        img_data = src.read()
        img_meta = src.meta
        rows = img_data.shape[1]
        columns = img_data.shape[2]
        transform = from_bounds(
            lon1, lat2, lon2, lat1, columns, rows
        )
        img_meta.update(
            {
                "driver": "GTiff",
                "height": img_data.shape[1],
                "width": img_data.shape[2],
                "transform": transform,
                "crs": "+proj=latlong",
            }
        )

        tif_path = str(base_dir / "out" / "geolocated.tif")
        with rasterio.open(tif_path, "w", **img_meta) as dst:
            dst.write(img_data)
    return True

def add_elevations_to_tiff(elevation_tif_path, rotation):
    if not os.path.exists(elevation_tif_path):
        print("yes")
        # merged_elevations_path = get_merged_elevation()

    if reproject_tiff(str(base_dir / "out" / "geolocated.tif"), str(base_dir / "out" / "geolocated_reproject.tif")):
        with rasterio.open(str(base_dir / "out" / "geolocated_reproject.tif")) as reproject_tif, rasterio.open(
            str(elevation_tif_path)
        ) as elevation_source:
            assert reproject_tif.crs == elevation_source.crs, "CRS mismatch between TIFF and DEM"

            source_elevation_data = elevation_source.read(1)
            max_elevation = np.max(source_elevation_data)

            # Initialize elevation band
            elevation_band = np.zeros((reproject_tif.height, reproject_tif.width), dtype=np.float32)
            # rotated_transform = rotate_transform(reproject_tif.transform, rotation, reproject_tif.width, reproject_tif.height)
            rotated_transform = reproject_tif.transform
            for row in range(reproject_tif.height):
                for col in range(reproject_tif.width):
                    # Convert TIFF pixel coordinates to geographic coordinates
                    lon, lat = pixel_to_geo(col, row, rotated_transform)

                    # DEM = Digital Elevation Model
                    # Convert geographic coordinates to DEM pixel coordinates
                    dem_col, dem_row = ~elevation_source.transform * (lon, lat)
                    dem_col, dem_row = int(dem_col), int(dem_row)

                    if 0 <= dem_row < elevation_source.height and 0 <= dem_col < elevation_source.width:
                        elevation_value = source_elevation_data[dem_row, dem_col]
                        corrected_elevation_value = max_elevation - elevation_value
                        elevation_band[row, col] = corrected_elevation_value
                        if row % 100 == 0 and col % 100 == 0: 
                            print(f"Original: {elevation_value}, Corrected: {corrected_elevation_value}")
            print("[INFO] Transformation rotation successful.")
            # Prepare updated TIFF metadata
            new_meta = reproject_tif.meta.copy()
            new_meta.update(count=reproject_tif.count + 1)

            print("[INFO] Transformation rotation successful2.")
            # Write updated TIFF
            with rasterio.open(
                str(base_dir / "out" / "geolocated_elevations.tif"), "w", **new_meta
            ) as new_tiff:
                for i in range(1, reproject_tif.count + 1):
                    new_tiff.write(reproject_tif.read(i), i)
                new_tiff.write(elevation_band, reproject_tif.count + 1)

        return True
    return False

def pixel_to_geo(x, y, transform):
    """Convert pixel coordinates to geographic coordinates using an affine transform."""
    return transform * (x, y)

def pixel_to_elevation(x, y):
    try:
        with rasterio.open(str(base_dir / "out" / "geolocated_elevations.tif")) as rasterio_tiff:
            elevation_band_index = rasterio_tiff.count
            elevation_value = rasterio_tiff.read(elevation_band_index)[y, x]
            return elevation_value
    except:
        print("Error in reading elevation value {x} {y}")
        return 0
    
def point_to_square_coordinates(x, y, width, height, transform):
    top_left_geo = pixel_to_geo(x, y, transform)
    top_right_geo = pixel_to_geo(x + width, y, transform)
    bottom_right_geo = pixel_to_geo(x + width, y + height, transform)
    bottom_left_geo = pixel_to_geo(x, y + height, transform)
    return (top_left_geo, top_right_geo, bottom_right_geo, bottom_left_geo)

def rotate_transform(transform, angle_degrees, img_width, img_height):
    # Reverse the rotation to align with original coordinates
    rotation_matrix = Affine.rotation(angle_degrees)
    # To rotate around the center of the image
    center_transform = (
        Affine.translation(-img_width / 2, -img_height / 2) *
        rotation_matrix *
        Affine.translation(img_width / 2, img_height / 2)
    )
    return transform * center_transform

def trim_transform(transform, trim_x, trim_y):
    return transform * Affine.translation(-trim_x, -trim_y)

def reproject_tiff(source_tif_path, output_tif_path):
    with rasterio.open(source_tif_path) as source_tif:
        # CRS = Coordinate Reference System

        # Calculate new parameters for new crs
        transform, width, height = calculate_default_transform(
            source_tif.crs, "EPSG:25830", source_tif.width, source_tif.height, *source_tif.bounds
        )

        # Update metadata
        metadata = source_tif.meta.copy()
        metadata.update(
            {
                "crs": "EPSG:25830",
                "transform": transform,
                "width": width,
                "height": height,
            }
        )

        with rasterio.open(output_tif_path, "w", **metadata) as destination:
            # Update each band
            for band in range(1, source_tif.count + 1):
                reproject(
                    source=rasterio.band(source_tif, band),
                    destination=rasterio.band(destination, band),
                    src_transform=source_tif.transform,
                    src_crs=source_tif.crs,
                    dst_transform=transform,
                    dst_crs="EPSG:25830",
                    resampling=Resampling.nearest,
                )
    return True
