"""
Conversion of transportation source files using JSON schemas to map columns.

Input: JSON source file (from which data file is read)
    Supported readable file types:
        * CSV (geom_types must be multilinestrings)
        * JSON
        * GeoJSON
        * Shapefile

Output: JSON data file
Usage: `python jsonprocessor.py ../generator/json/filename`


TODO before running:
    -- Copy data from minio (./cp_input.sh)
    -- Rearrange file order (Remove CD/CSD from file path and move to input/)
    -- Move variablemap.csv to generator/
"""
import sys
import json
import pandas as pd
import geopandas as gpd
import funcs
from shapely.geometry import Point


# Read source mappings from bash argument
jsonFile = sys.argv[1]
with open(jsonFile, "r") as f:
    print("Converting JSON encoded data into Python dictionary...")
    srcmap = json.load(f)


# Path to files
reg = srcmap['force']['prov/terr'].upper()
foldername = f"{funcs.codeConverter(reg)} - {reg.upper()}"

## Subfolder dict for class
# TODO: convert variety in variablemaps to standards
d = {
    'multi-use' : 'Mixed', 
    'multi' : 'Mixed',
    'mixed' : 'Mixed',
    'walking' : 'Pedestrian',
    'cycling' : 'Cycling',
    'biking' : 'Cycling'
    }
subfolder = d[srcmap['class']]

# fpath = f"~/INFC/input/temp_files/{foldername}/*/{srcmap['force']['municipality'].title().replace(' ', '')}/*/"
fpath = f"input/{foldername}/{srcmap['force']['municipality']}/{subfolder}/"


# Read file according to file type, convert to GeoDataFrame, and set/reproject crs
if srcmap['filetype'] == 'json':
    df = pd.read_json(fpath + srcmap['filename'])
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326",
                           geometry=srcmap['schema']['geometry'])

elif srcmap['filetype'] == 'csv':
    df = pd.read_csv(fpath + srcmap['filename'])
    geometry = gpd.GeoSeries.from_wkt(df[srcmap['schema']['geometry']])
    gdf = gpd.GeoDataFrame(df, crs = 'EPSG:4326',
                           geometry = geometry)

elif srcmap['filetype'] in ['shp', 'geojson']:
    gdf = gpd.read_file(fpath + srcmap['filename'])
    gdf = gdf.to_crs("EPSG:4326")

else:
    print(f"File type {srcmap['filetype']} not supported.")


# Filter out non-operational/inactive ----
if 'inscope_filter' in srcmap['filter'].keys():
    gdf.loc[gdf[f"{srcmap['filter']['inscope_filter']}"] == f"{srcmap['filter']['inscope_value']}"]


# Subset, clean columns & export as GeoJSON
if srcmap['class'] == 'multi-use':
    funcs.multi(jsonFile, srcmap, gdf)

if srcmap['class'] == 'biking':
    gdf = funcs.process_columns(srcmap, gdf, new_class = 'biking')
    gdf.to_file(f'output/biking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")

if srcmap['class'] == 'walking':
    gdf = funcs.process_columns(srcmap, gdf, new_class = 'walking')
    gdf.to_file(f'output/walking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")


print("Done.")
