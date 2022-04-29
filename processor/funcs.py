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


def contains_func(v, geodataframe, k):
    """
    When filtering using str.contains.

    v = value from sourcemap filter value.
    k = value from sourcemap filter column.
    """
    if isinstance(v,list):  # Seems to be better than type(x) == y
        v = [x.split("Contains ")[1] for x in v]
        return geodataframe.loc[geodataframe[k].fillna("").str.contains("|".join(v), case = False)]
        
    else:
        v = v.split("Contains ")[1]
        return geodataframe.loc[geodataframe[k].fillna("").str.contains(v, case = False)]



def multi(jsonFile, sourcemap, geodataframe, log):
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
                        if "contains" in v.lower():
                            v = v.split("__")
                            walking = contains_func(v, geodataframe, k)
                        else:
                            v = v.split("__")
                            walking = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x in v)]

                    elif "contains" in v.lower():
                        walking = contains_func(v, geodataframe, k)

                    else:
                        walking = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x == v)]

                    print("Exporting filtered walking data...")
                    walking_out = process_columns(sourcemap, walking, new_class = "walking")
                    walking_out.to_file(f'output/walking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")
                    
                    # Log
#                     log['output_length'].append(len(walking_out))


                elif export_dict[key] == "biking":

                    # Filter by several or one value(s)
                    if "__" in v:
                        if "contains" in v.lower():
                            v = v.split("__")
                            biking = contains_func(v, geodataframe, k)
                        else:
                            v = v.split("__")
                            biking = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x in v)]

                    elif "contains" in v.lower():
                        biking = contains_func(v, geodataframe, k)

                    else:
                        biking = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x == v)]

                    print("Exporting filtered biking data...")
                    biking_out = process_columns(sourcemap, biking, new_class = "biking")
                    biking_out.to_file(f'output/biking/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")

                    # Log
#                     log['output_length'].append(len(biking_out))
                    
                elif export_dict[key] == "multi":
                    print("Exporting filtered multi data...")

                    # Filter by several or one value(s)
                    if "__" in v:
                        if "contains" in v.lower():
                            v = v.split("__")
                            multi = contains_func(v, geodataframe, k)
                        else:
                            v = v.split("__")
                            multi = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x in v)]

                    elif "contains" in v.lower():
                        multi = contains_func(v, geodataframe, k)

                    else:
                        multi = geodataframe.loc[geodataframe[k].fillna("").map(lambda x: x == v)]


                    multi_out = process_columns(sourcemap, multi, new_class = "multi-use")
                    multi_out.to_file(f'output/multi-use/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")
                    
                    # Log
#                     log['output_length'].append(len(multi_out))
    else:
        print("Exporting multi data...")
        multi_out = process_columns(sourcemap, geodataframe, new_class = "multi-use")
        multi_out.to_file(f'output/multi-use/{jsonFile.split("/")[-1].split(".")[0]}.geojson', driver="GeoJSON")
                            
        # Log
#         log['output_length'].append(len(multi_out))
            