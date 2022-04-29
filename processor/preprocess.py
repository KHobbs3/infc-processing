"""
Run before jsonprocessor.py.
For 
    * West Vancouver source_class
    * Montreal surface_type
    * Toronto B
"""

import numpy as np
import geopandas as gpd
import glob


def rplc(string):
    """
    To substitute string with None value in pre-processing.
    """
    if string == "n/a (one-way street, no 'L' route)" or string == "Non applicable" or string == "NULL":
        return None
    else:
        return string

def int_to_str(x):
    """
    For Toronto sidewalk data where multiuse column is 0, 1 in orig data.
    
    """
    if x == 0:
        return "no"
    if x == 1:
        return "yes"
    

for file in glob.glob("input/*/*/*/*.shp"):
    if file == "input/59 - BC/West Vancouver/Cycling/ROADS_CYCLE_ROUTES.shp":
        print("Processing West Vancouver...")
        # Read file
        gdf = gpd.read_file(file)

        # Replace text NAs with None
        gdf.FACILITY_L = gdf.FACILITY_L.map(rplc)

        # Fill missing values on left with right
        gdf.FACILITY_L.fillna(gdf.FACILITY_R, inplace = True)

        # Where left and right mismatch, concatenate
        gdf["source_cla"] = np.where(gdf["FACILITY_L"] != gdf["FACILITY_R"], 
                                       gdf["FACILITY_L"]+"/"+gdf["FACILITY_R"], 
                                       gdf['FACILITY_L'])
        # Export
        gdf.to_file("input/59 - BC/West Vancouver/Cycling/ROADS_CYCLE_ROUTES_processed.shp")


    if file == "input/24 - QC/Montreal/Pedestrian/VOI_TROTTOIR_S_T12.shp":
        print("Processing Montreal...")

        # Read file
        gdf = gpd.read_file(file)

        # Replace text missing values with None
        gdf.MATERIAUIN = gdf.MATERIAUIN.map(rplc)
        gdf.MATERIAUTR = gdf.MATERIAUTR.map(rplc)
        gdf.MATERIAUBO = gdf.MATERIAUBO.map(rplc)

        # Fill MATERIAUIN with other columns
        gdf['srfc_type'] = gdf.MATERIAUIN.fillna(gdf.MATERIAUTR)
        gdf.srfc_type.fillna(gdf.MATERIAUBO, inplace = True)

        # Export
        gdf.to_file("input/24 - QC/Montreal/Pedestrian/VOI_TROTTOIR_S_T12_processed.shp")


    if file == "input/35 - ON/Toronto/Mixed/Bike network data.shp":
        print("Processing Toronto...")

        # Read file
        gdf = gpd.read_file(file)

        # TODO:
        # PROCESS TORONTO BIKING
        # Not sure how to do this exactly but basically we use Field 20 and fill any blanks with Field 15
        gdf['source_cla'] = gdf.FIELD_20.fillna(gdf.FIELD_15) # I think this is right?? >> Perfect!! - KT

        # Export
        gdf.to_file("input/35 - ON/Toronto/Mixed/Bike network data_processed.shp")
        
    if file == "input/35 - ON/Toronto/Mixed/Sidewalk_Inventory_wgs84.shp":
        print("Processing Toronto...")

        # Read file
        gdf = gpd.read_file(file)

        gdf['Multiuse'] = gdf['Multiuse'].map(int_to_str)
        # Export
        gdf.to_file("input/35 - ON/Toronto/Mixed/Sidewalk_Inventory_wgs84_processed.shp")


    if file == "input/35 - ON/Niagara Falls/Cycling/community-bike-lanes.shp":
        print("Processing Niagara...")

        # Read file & set CRS
        gdf = gpd.read_file(file)
        gdf = gdf.set_crs("EPSG:4326")

        # Export
        gdf.to_file("input/35 - ON/Niagara Falls/Cycling/community-bike-lanes_processed.shp")

    if file == "input/35 - ON/Niagara Falls/Mixed/community-public-trails.shp":
        print("Processing Niagara...")

        # Read file & set CRS
        gdf = gpd.read_file(file)
        gdf = gdf.set_crs("EPSG:4326")

        # Export
        gdf.to_file("input/35 - ON/Niagara Falls/Mixed/community-public-trails_processed.shp")
        
#     if file == "input/59 - BC/North Vancouver/Cycling/TrnBiking.sh":
#         print("Processing North Vancouver...")
#         gdf = gpd.read_file(file)
#         gdf[gdf.STATUS_RES.str.contains("Existing")]


print("Done.")