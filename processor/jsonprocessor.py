"""
Conversion of transportation source files using JSON schemas to map columns.

Input: JSON source file (from which data file is read)
    Supported readable file types:
        * CSV
        * JSON
        * GeoJSON
        * Shapefile

Output: JSON data file
Usage: `python jsonprocessor.py ../generator/json/filename`

"""
import sys
import json
import pandas as pd
import geopandas as gpd
from funcs import *

# Read source mappings from bash argument
jsonFile = sys.argv[1]
with open(jsonFile, "r") as f:
    print("Converting JSON encoded data into Python dictionary.")
    srcmap = json.load(f)


# Path to files --- SUBJECT TO CHANGE WITH VAR MAP
reg = srcmap['prov/terr'].split(":")[1].upper()
foldername = "{} - {}".format(codeConverter(reg), reg.upper())
fpath = "input/{}/{}/".format(foldername, srcmap['municipality'].replace(' ', '').split(":")[1].title())


# Read file according to file type and convert to GeoDataFrame
if srcmap['filetype'] == 'csv':
    df = pd.read_csv(fpath + srcmap['filename'])
    gdf = geopandas.GeoDataFrame(df,
        geometry=srcmap['schema']['address']['geometry'])

elif srcmap['filetype'] == 'json':
    df = pd.read_json(fpath + srcmap['filename'])
    gdf = geopandas.GeoDataFrame(df,
        geometry=srcmap['schema']['address']['geometry'])

elif srcmap['filetype'] == 'shp':
    gdf = gpd.read_file(fpath + srcmap['filename'])

elif srcmap['filetype'] == 'geojson':
    gdf = gpd.read_file(fpath + srcmap['filename'], driver = "GeoJSON")

else:
    print("File type % not supported." % srcmap['filetype'])


# Rename columns according to schema
gdf.rename(columns = srcmap['schema']['infrastructure'], inplace = True)
gdf.rename(columns = srcmap['schema']['address'], inplace = True)


# Set forced columns as fixed values
for key, value in srcmap.items():
    if _isForceValue(value):
        gdf[key] = value.split(':')[1]

# filter data
# df.query['%' % df[srcmap['separate']['filter_column']] srcmap['separate']['filter_value']]

# repeat rows for class columns?
# if type(srcmap['class']) == list():
#     # TODO: duplicate entire data set?
# else:
#     df['class'] = srcmap['class']


# Export as GeoJSON
df.to_file('output/%.geojson' % jsonFile.strip('.')[0], driver = "GeoJSON", index = False)
