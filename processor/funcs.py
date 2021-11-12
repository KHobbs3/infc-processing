# Functions used in jsonprocessor.py.
import pandas as pd
import re

def codeConverter(value):
        """Converts province or territory 2-letter alpha code to corresponding SGC code."""
        d = pd.read_csv("input/prov-terr.csv").set_index("Alpha_codes")['SGC_code'].to_dict()
        return d[value]

def isForceValue(value):
        """Returns True if value contains the prefix 'force:'."""
        FORCE_REGEXP = re.compile(r'force:.*', re.UNICODE)
        return bool(FORCE_REGEXP.match(value))

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
