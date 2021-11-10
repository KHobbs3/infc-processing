"""
Creates JSON source files for opentabulate according to a variable map csv.

File organization:
    dir/
        json/ (output folder for src files.)
        variablemap.csv
        jsongenerator.py
"""

import csv


def main():
    infraFields = ['source_id', 'source_class', 'surface_type', 'width']
    addressFields = ['street_name', 'geometry']
    forceFields = ['prov/terr', 'municipality', 'provider', 'source_url', 'licence']
    input_file = csv.DictReader(open('variablemap.csv'))

    for row in input_file:
        if row['subclass'] != "":
                OP = open("json/" + row['municipality'].lower().replace(' ', '-')
                                + "-" + row['class'].lower()
                                + "-" + row['subclass'].lower()
                                + ".json","w")
        else:
                OP = open("json/" + row['municipality'].lower().replace(' ', '-')
                                + "-" + row['class'].lower()
                                + ".json","w")

        # General information -----
        OP.write('{ \n')
        OP.write('    "filename": "' + row['file_name'] + '.' + row['format'] + '",\n')
        OP.write('    "filetype": "' + row['format'] + '",\n')

        if row['class'] == 'multi-use':
            OP.write('    "class": ' + '["walking", "biking"],\n')
        else:
            OP.write('    "class": "' + row['class'] + '",\n')

        if row['filter_exclude'] != "":
            OP.write('    "separate": {\n' +
                    '           "filter_column": "' + row['filter_exclude'] + '",\n'
                    '           "filter_value": "' + row['filter_value'] + '"\n' +
                        '},\n')
        first = True
        other = False
        force = False

        for f in forceFields:
            # if row[f] != '':
            #     if first:
                    # OP.write('    "'+ f +'": "force:' + row[f] + '"')
                    # first = False
                # else:
            OP.write('    "'+ f +'": "force:' + row[f] + '"')
            OP.write(',\n')

            force = True

        OP.write('    "schema": {\n')
        # Infrastructure fields ------
        OP.write('        "infrastructure": {\n')
        for f in infraFields:
            if row[f] != '':
                if first:
                    first = False
                else:
                    OP.write(',\n')
                OP.write('          "'+ f +'": "' + row[f] + '"')
                other = True

        OP.write('  \n}')

        if not first:
            OP.write(',\n')
        add = False

        # Address fields --------
        for f in addressFields:
            if row[f] != '':
                add = True
        if add:
            # if other or force:
                # OP.write(',\n')
            OP.write('         "address": {\n')
            first = True

            for f in addressFields:
                if row[f] != '':
                    if first:
                        first = False
                    else:
                        OP.write(',\n')
                    OP.write('            "'+ f + '": "' + row[f] + '"')
            OP.write('\n        }\n')
        OP.write('    }\n')

        OP.write('}')
        OP.close()

if __name__ == "__main__":
    main()
