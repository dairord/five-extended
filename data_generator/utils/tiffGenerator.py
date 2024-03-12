from datetime import datetime
import rasterio
from rasterio.transform import from_bounds

global name, lat1, lon1, lat2, lon2


def generate_tiff(name, lat1, lon1, lat2, lon2):

    with rasterio.open(name) as src:
        img_data = src.read()
        img_meta = src.meta

        transform = from_bounds(
            lon1, lat2, lon2, lat1, img_data.shape[2], img_data.shape[1]
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
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        tiff_name = "geolocated.tiff"
        print("yay")
        with rasterio.open(tiff_name, "w", **img_meta) as dst:
            print("notyay")
            dst.write(img_data)
    return True


def pixel_to_geo(x, y, transform):
    longitude = transform[0] * x + transform[1] * y + transform[2]
    latitude = transform[3] * x + transform[4] * y + transform[5]
    return (longitude, latitude)


def point_to_square_coordinates(x, y, w, h, t):
    top_left_geo = pixel_to_geo(x, y, t)
    top_right_geo = pixel_to_geo(x + w, y, t)
    bottom_right_geo = pixel_to_geo(x + w, y + h, t)
    bottom_left_geo = pixel_to_geo(x, y + h, t)
    return (top_left_geo, top_right_geo, bottom_right_geo, bottom_left_geo)
