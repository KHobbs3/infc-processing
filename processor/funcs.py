# Functions used in jsonprocessor.py.
import pandas as pd
# import re


def codeConverter(value):
    """Converts province or territory 2-letter alpha code to corresponding SGC code."""
    d = pd.read_csv("input/prov-terr.csv").set_index("Alpha_codes")['SGC_code'].to_dict()
    return d[value]


def drop_cols(sourcemap, geodataframe):
    """Creates a geodataframe only retaining only field names referred to in the source map JSON file."""
    cols = []

    for key in sourcemap.keys():
        if key != "schema":
            cols.append(key)
        else:
            for k in sourcemap['schema']:
                cols.append(k)

    return geodataframe.drop(geodataframe.columns.difference(cols), 1)


def process_columns(sourcemap, geodataframe, new_class):
    # Rename columns according to schema
    if sourcemap['filetype'] == 'csv':
        cols_dict = {v: k for k, v in sourcemap['schema'].items()} # Replace csv column names with varmap field names
        cols_dict.pop(sourcemap['schema']['geometry']) # New geometry column made during conversion to gdf
    else:
        cols_dict = {v: k for k, v in sourcemap['schema'].items()}

    geodataframe.rename(columns=cols_dict, inplace = True)

    # Drop unnessary columns
    geodataframe = drop_cols(sourcemap, geodataframe)

    # Set forced columns as fixed values
    for key, value in sourcemap['force'].items():
        geodataframe[key] = value

    # Add class column
    geodataframe['class'] = new_class

    # Return
    return geodataframe


export_dict = {
    'walk_value': 'walking',
    'bike_value': 'biking',
    'multi_value': 'multi'
}


def multi(jsonFile, sourcemap, geodataframe):
    """
    Filters geodataframe with a "multi-use" class
    according to walking, biking, multi column filters, if filled.

    Exports to appropriate biking or walking output subfolders.

    Where no filtering is required, multi-use file is exported twice (once to each subdirectory)/
    """
    if bool(sourcemap['filter'].keys()):
        for key in sourcemap['filter'].keys():
            if key in ["walk_column", "bike_column", "multi_column"] and sourcemap['filter'][key] != "":
                k = sourcemap['filter'][key]
            # Can we do something here like make dict pairs of each col,val and refer to those?
            if key in ["walk_value", "bike_value", "multi_value"] and sourcemap['filter'][key] != "":
                v = sourcemap['filter'][key]

                # Filter & export subsets
                if export_dict[key] == "walking":
                    # Filter by several or one value(s)
                    if "__" in v:
                        v = v.split("__")
                        walking = geodataframe.loc[geodataframe[k].map(lambda x: x in v)]
                    elif "contains" in v.lower():
                        v = v.lower().split("contains ")[1]
                        walking = geodataframe[k].str.contains(v)

                    else:
                        walking = geodataframe.loc[geodataframe[k].map(lambda x: x == v)]

                    print("Exporting filtered walking data...")
                    process_columns(sourcemap, walking, new_class = "walking")\
                        .to_file(f'output/walking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")

                elif export_dict[key] == "biking":

                    # Filter by several or one value(s)
                    if "__" in v:
                        v = v.split("__")
                        biking = geodataframe.loc[geodataframe[k].map(lambda x: x in v)]

                    elif "contains" in v.lower():
                        v = v.lower().split("contains ")[1]
                        biking = geodataframe[k].str.contains(v)

                    else:
                        biking = geodataframe.loc[geodataframe[k].map(lambda x: x == v)]

                    print("Exporting filtered biking data...")
                    process_columns(sourcemap, biking, new_class = "biking")\
                        .to_file(f'output/biking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")

                elif export_dict[key] == "multi":
                    print("Exporting filtered multi data...")

                    # Filter by several or one value(s)
                    if "__" in v:
                        v = v.split("__")
                        multi = geodataframe.loc[geodataframe[k].map(lambda x: x in v)]

                    elif "contains" in v.lower():
                        v = v.lower().split("contains ")[1]
                        multi = geodataframe[k].str.contains(v)

                    else:
                        multi = geodataframe.loc[geodataframe[k].map(lambda x: x == v)]


                    process_columns(sourcemap, multi, new_class = "multi-use")\
                        .to_file(f'output/multi/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")

    else:
        print("Exporting multi data...")
        process_columns(sourcemap, geodataframe, new_class = "multi-use")\
            .to_file(f'output/multi/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")
