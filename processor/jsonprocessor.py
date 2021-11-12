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
fpath = "input/{}/{}/".format(foldername, srcmap['municipality'].title().replace(' ', '').split(":")[1])


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
cols_dict = {v: k for k, v in srcmap['schema'].items()}
gdf.rename(columns = cols_dict, inplace = True)


# Set forced columns as fixed values
for key, value in srcmap.items():
    try:
        if isForceValue(value):
            try:
                gdf[key] = value.split(':')[1] + value.split(':')[2]
            except IndexError:
                gdf[key] = value.split(':')[1]
    except TypeError:
        continue

# filter data
    #TODO: update logic based on variablemap.csv ----
if srcmap['separate']:
    gdf.query('{} == {}'\
              .format(srcmap['separate']['filter_column'], srcmap['separate']['filter_value']),
                  inplace = True)


# Drop unnessary columns
gdf = drop_cols(srcmap, gdf)


# Add class column
if type(srcmap['class']) == list():
    # TODO: duplicate entire data set? ----
else:
    df['class'] = srcmap['class']


# Export as GeoJSON
    #TODO: find better way to name out files ----
gdf.to_file('output/{}.json'.format(jsonFile.split("/")[3].split('.')[0]))
print("Done.")
