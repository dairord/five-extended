from pathlib import Path
from osgeo import gdal
base_dir = Path(__file__).parent.parent

def standardize_data_type(dem_file, target_data_type=gdal.GDT_Float32):
    converted_file = dem_file.replace('.tif', '_converted.tif')
    
    dataset = gdal.Open(dem_file, gdal.GA_ReadOnly)
    
    gdal.Translate(converted_file, dataset, outputType=target_data_type)
    
    dataset = None  

    return converted_file

def print_dem_statistics(dem_file):
    dataset = gdal.Open(dem_file)
    band = dataset.GetRasterBand(1)
    stats = band.GetStatistics(True, True)
    print(f"Statistics for {dem_file}:")
    print(f"Min={stats[0]}, Max={stats[1]}, Mean={stats[2]}, StdDev={stats[3]}")
    dataset = None  


dem_files = ['your_new_filename.tif', 'your_new_filename2.tif']
converted_dem_files = [standardize_data_type(dem) for dem in dem_files]

for dem in converted_dem_files:
    print_dem_statistics(dem)


vrt_options = gdal.BuildVRTOptions(resampleAlg='bilinear', addAlpha=False)
vrt_filename = 'merged.vrt'
gdal.BuildVRT(vrt_filename, converted_dem_files, options=vrt_options)

merged_dem_filename = 'merged_dem.tif'
gdal.Translate(merged_dem_filename, vrt_filename)
print_dem_statistics(merged_dem_filename)
