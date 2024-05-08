from datetime import datetime
import os
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import box
import numpy as np
from pathlib import Path

global name, lat1, lon1, lat2, lon2
base_dir = Path(__file__).parent.parent


def generate_tiff(image_path, lat1, lon1, lat2, lon2):

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


def add_elevations_to_tiff():
    if not os.path.exists(str(base_dir / "utils" / "spain.tif")):
        print("yes")
        # merged_elevations_path = get_merged_elevation()
        
    if reproject_tiff(str(base_dir / "out" / "geolocated.tif"), str(base_dir / "out" / "geolocated_reproject.tif")):
        with rasterio.open(str(base_dir / "out" / "geolocated_reproject.tif")) as reproject_tif, rasterio.open(
            str(base_dir / "utils" / "spain.tif")
        ) as elevation_source:
            assert reproject_tif.crs == elevation_source.crs, "CRS mismatch between TIFF and DEM"

            source_elevation_data = elevation_source.read(1)
            max_elevation = np.max(source_elevation_data)

            # Initialize elevation band
            elevation_band = np.zeros((1, reproject_tif.height, reproject_tif.width), dtype=np.float32)

            for row in range(reproject_tif.height):
                for col in range(reproject_tif.width):
                    # Convert TIFF pixel coordinates to geographic coordinates
                    lon, lat = pixel_to_geo(col, row, reproject_tif.transform)

                    # DEM = Digital Elevation Model
                    # Convert geographic coordinates to DEM pixel coordinates
                    dem_col, dem_row = ~elevation_source.transform * (lon, lat)
                    dem_col, dem_row = int(dem_col), int(dem_row)

                    if 0 <= dem_row < elevation_source.height and 0 <= dem_col < elevation_source.width:
                        elevation_value = source_elevation_data[dem_row, dem_col]
                        corrected_elevation_value = max_elevation - elevation_value
                        elevation_band[0, row, col] = corrected_elevation_value
                        if row % 100 == 0 and col % 100 == 0:  # Adjust sampling as needed
                            original_value = source_elevation_data[dem_row, dem_col]
                            corrected_value = max_elevation - original_value
                            print(f"Original: {original_value}, Corrected: {corrected_value}")

            # Prepare updated TIFF metadata
            new_meta = reproject_tif.meta.copy()
            new_meta.update(count=reproject_tif.count + 1)

            # Write updated TIFF
            with rasterio.open(
                str(base_dir / "out" / "geolocated_elevations.tif"), "w", **new_meta
            ) as new_tiff:
                new_tiff.write(reproject_tif.read(), indexes=range(1, reproject_tif.count + 1))
                new_tiff.write(elevation_band[0, :, :], reproject_tif.count + 1)

        return True
    return False


def pixel_to_geo(x, y, transform):
    longitude = transform[0] * x + transform[1] * y + transform[2]
    latitude = transform[3] * x + transform[4] * y + transform[5]
    return (longitude, latitude)


def pixel_to_elevation(x, y):
    
    with rasterio.open(str(base_dir / "out" / "geolocated_elevations.tif")) as rasterio_tiff:
        elevation_band_index = rasterio_tiff.count
        elevation_value = rasterio_tiff.read(elevation_band_index)[y, x]
        return elevation_value


def point_to_square_coordinates(x, y, w, h, t):
    top_left_geo = pixel_to_geo(x, y, t)
    top_right_geo = pixel_to_geo(x + w, y, t)
    bottom_right_geo = pixel_to_geo(x + w, y + h, t)
    bottom_left_geo = pixel_to_geo(x, y + h, t)
    return (top_left_geo, top_right_geo, bottom_right_geo, bottom_left_geo)


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
