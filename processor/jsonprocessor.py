"""
Conversion of transportation source files using JSON schemas to map columns.

Input: JSON source file (from which data file is read)
    Supported readable data file types:
        * CSV
        * JSON
        * GeoJSON
        * Shapefile

Output: JSON data file
Usage: `python jsonprocessor.py ../generator/json/filename`
    or
    ./run_all.sh

Before running this script:
    -- Copy data and variable maps from minio (./cp_input.sh)
    -- Rearrange file order (Remove CD/CSD from file path and move to input/)
    -- Run `python make_vmap.py` in generator/
    -- Run `python jsongenerator.py` in generator/
"""
import sys
import json
import pandas as pd
import geopandas as gpd
import funcs
from shapely.geometry import Point
import warnings


# --- SET UP --- #
warnings.filterwarnings("ignore")
log = {
    'file': [],
    'input_length' : [],
    'output_length' : []
  }

# Read source mappings from bash argument
jsonFile = sys.argv[1]
with open(jsonFile, "r") as f:
    print("Converting JSON encoded data into Python dictionary...")
    srcmap = json.load(f)


# Path to files
reg = srcmap['force']['prov/terr'].upper()
foldername = f"{funcs.codeConverter(reg)} - {reg.upper()}"

# Subfolder dict for class
d = {
    'multi-use' : 'Mixed', 
    'walking' : 'Pedestrian',
    'biking' : 'Cycling'
    }
subfolder = d[srcmap['class']]

fpath = f"input/{foldername}/{srcmap['force']['municipality']}/{subfolder}/"


# --- PROCESSING --- #

    
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


# Log for inscope changes
log['file'].append(jsonFile.split("/")[-1].split(".")[0])
log['input_length'].append(len(gdf))

# Filter out non-operational/inactive ----
if 'inscope_filter' in srcmap['filter'].keys():
    k = srcmap['filter']['inscope_filter']
    v = srcmap['filter']['inscope_value']
    if "__" in v:
        if "contains" in v.lower():
            v = v.split("__")
            gdf = funcs.contains_func(v, gdf, k)
        else:
            v = v.split("__")
            gdf = gdf.loc[gdf[k].fillna("").map(lambda x: x in v)]
        print(len(gdf))

    elif "contains" in v.lower():
        gdf = funcs.contains_func(v, gdf, k)
        print(len(gdf))

    else:
        gdf = gdf.loc[gdf[k] == v]
        print(len(gdf))

# Log
log['output_length'].append(len(gdf))
pd.DataFrame(log).to_csv(f'_log/{jsonFile.split("/")[-1].split(".")[0]}.csv', index = False)

# Subset, clean columns & export as GeoJSON
if srcmap['filter'].keys():
    funcs.multi(jsonFile, srcmap, gdf, log)

elif srcmap['class'] == 'biking':
    gdf = funcs.process_columns(srcmap, gdf, new_class = 'biking')
    gdf.to_file(f'output/biking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")


elif srcmap['class'] == 'walking':
    gdf = funcs.process_columns(srcmap, gdf, new_class = 'walking')
    gdf.to_file(f'output/walking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")


print("Done.")
