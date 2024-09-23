import json
import os
import requests
import numpy as np
import threading
import cv2

file_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(file_dir)
prefs_path = os.path.join(parent_dir, "preferences.json")

headers = {
    
}

maptiler_url = "https://api.maptiler.com/maps/satellite/256/{z}/{x}/{y}.jpg?key={key}"
google_url = (
    # "https://maps.googleapis.com/maps/api/staticmap?center={y},{x}&zoom={z}&size=256x256&maptype=satellite&key={key}&sessiontoken={token}"
    "https://tile.googleapis.com/v1/2dtiles/{z}/{x}/{y}?session={token}&key={key}"
)


def download_tile(url, headers, channels):
    # print(url)
    response = requests.get(url, headers=headers)
    arr = np.asarray(bytearray(response.content), dtype=np.uint8)

    if channels == 3:
        return cv2.imdecode(arr, 1)
    return cv2.imdecode(arr, -1)


def project_with_scale(lat: float, lon: float, scale):
    siny = np.sin(lat * np.pi / 180)
    siny = min(max(siny, -0.9999), 0.9999)
    x = scale * (0.5 + lon / 360)
    y = scale * (0.5 - np.log((1 + siny) / (1 - siny)) / (4 * np.pi))
    return x, y


def download_image(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    search_motor: list,
    zoom: int = 21,
    tile_size: int = 256,
    channels: str = 3,
) -> np.ndarray:
    """
    Downloads a map region. Returns an image stored either in BGR or BGRA as a `numpy.ndarray`.

    Parameters
    ----------
    `(lat1, lon1)` - Coordinates (decimal degrees) of the top-left corner of a rectangular area

    `(lat2, lon2)` - Coordinates (decimal degrees) of the bottom-right corner of a rectangular area

    `zoom` - Zoom level

    `url` - Tile URL with {x}, {y} and {z} in place of its coordinate and zoom values

    `headers` - Dictionary of HTTP headers

    `tile_size` - Tile size in pixels

    `channels` - Number of channels in the output image. Use 3 for JPG or PNG tiles and 4 for PNG tiles.
    """

    with open(os.path.join(parent_dir, "preferences.json"), "r", encoding="utf-8") as f:
        prefs = json.loads(f.read())

    selected_motor_index = 0
    session_token = None
    for index, motor in enumerate(search_motor):
        if motor == True:
            selected_motor_index = index
            break

    match selected_motor_index:
        case 0:
            url = google_url
            response = requests.post(
                "https://tile.googleapis.com/v1/createSession?key="
                + prefs["google_api_key"],
                headers={"Content-type": "application/json"},
                json={"mapType": "satellite", "language": "en-US", "region": "US"},
            )
            session_token = response.json()["session"]
            key = prefs["google_api_key"]
            # url.format(token=session_token, key=prefs["google_api_key"])
        case 1:
            url = maptiler_url
            key = prefs["maptiler_api_key"]
            # url.format(key=prefs["maptiler_api_key"])

    scale = 1 << zoom

    # Find the pixel coordinates and tile coordinates of the corners
    tl_proj_x, tl_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    tl_pixel_x = int(tl_proj_x * tile_size)
    tl_pixel_y = int(tl_proj_y * tile_size)
    br_pixel_x = int(br_proj_x * tile_size)
    br_pixel_y = int(br_proj_y * tile_size)

    tl_tile_x = int(tl_proj_x)
    tl_tile_y = int(tl_proj_y)
    br_tile_x = int(br_proj_x)
    br_tile_y = int(br_proj_y)

    img_w = abs(tl_pixel_x - br_pixel_x)
    img_h = br_pixel_y - tl_pixel_y
    img = np.ndarray((img_h, img_w, channels), np.uint8)  # type: ignore

    def build_row(row_number):
        for j in range(tl_tile_x, br_tile_x + 1):
            if session_token is not None:
                tile = download_tile(
                    url.format(x=j, y=row_number, z=zoom, token=session_token, key=key),
                    headers,
                    channels,
                )
            else:
                tile = download_tile(
                    url.format(x=j, y=row_number, z=zoom, key=key), headers, channels
                )

            # Find the pixel coordinates of the new tile relative to the image
            tl_rel_x = j * tile_size - tl_pixel_x
            tl_rel_y = row_number * tile_size - tl_pixel_y
            br_rel_x = tl_rel_x + tile_size
            br_rel_y = tl_rel_y + tile_size

            # Define where the tile will be placed on the image
            i_x_l = max(0, tl_rel_x)
            i_x_r = min(img_w + 1, br_rel_x)
            i_y_l = max(0, tl_rel_y)
            i_y_r = min(img_h + 1, br_rel_y)

            # Define how border tiles are cropped
            cr_x_l = max(0, -tl_rel_x)
            cr_x_r = tile_size + min(0, img_w - br_rel_x)
            cr_y_l = max(0, -tl_rel_y)
            cr_y_r = tile_size + min(0, img_h - br_rel_y)

            img[i_y_l:i_y_r, i_x_l:i_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]

    threads = []
    for i in range(tl_tile_y, br_tile_y + 1):
        thread = threading.Thread(target=build_row, args=[i])
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return img
