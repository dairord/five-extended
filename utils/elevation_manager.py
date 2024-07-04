from io import BytesIO
import os
from pathlib import Path
import tempfile
import rasterio
from rasterio.io import MemoryFile
from rasterio.merge import merge
import time
from utils.CNIGDownloader import download_elevation
from utils.CNIGIndexer import getIndex
import matplotlib.pyplot as plt
import re

base_dir = Path(__file__).parent.parent

def get_tif_list(elevation_indexes):
    if isinstance(elevation_indexes, bytes):
        elevation_indexes = elevation_indexes.decode('utf-8')
    pattern = r'linkDescDir_([a-zA-Z0-9]+)'
    matches = re.findall(pattern, elevation_indexes)
    return matches

def plot_elevation_map(mosaic, title="Elevation Map"):
    plt.figure(figsize=(10, 10))
    plt.imshow(mosaic[0], cmap='terrain')
    plt.colorbar(label='Elevation')
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

def start_elevation_download(coordinates, resolution_code):
    elevation_indexes = getIndex(coordinates, resolution_code)
    while elevation_indexes is None:
        print("INDEXER")
        time.sleep(100)
        elevation_indexes = getIndex(coordinates, resolution_code)
    
    elevation_indexes = get_tif_list(elevation_indexes)
    
    elevation_data = []
    for index in elevation_indexes:
        area = download_elevation(index, resolution_code)
        while area is None:
            time.sleep(100)
            area = download_elevation(index, resolution_code)
        elevation_data.append(area)

    temp_files = []
    for elevation in elevation_data:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tif')
        temp_file.write(elevation)
        temp_file.flush() 
        temp_files.append(temp_file)

    tif_files = [rasterio.open(temp_file.name) for temp_file in temp_files]

    if tif_files.__len__() == 0: 
        return None
    
    merged_data, out_trans = merge(tif_files)

    # plot_elevation_map(merged_data)

    merged_path = str(base_dir / "elevations" / "area_elevation.tif")
    
    
    with rasterio.open(
        merged_path, 'w',
        driver='GTiff',
        height=merged_data.shape[1],
        width=merged_data.shape[2],
        count=merged_data.shape[0],  
        dtype=merged_data.dtype,
        crs=tif_files[0].crs,
        transform=out_trans
    ) as dest:
        for i in range(1, merged_data.shape[0] + 1):
            dest.write(merged_data[i-1], i)

    for tif in tif_files:
        tif.close()
    
    # Clean up temporary files
    for temp_file in temp_files:
        temp_file.close()
        os.remove(temp_file.name)
    
    return merged_path