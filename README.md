# infc-processing
Scripts to generate standardized GeoJSON files from various sources.

1. Fill variablemap.csv in generator/
2. Run `python jsongenerator.py` to create JSONs for each data source.
3. Run `python jsonprocessor.py ../generator/json/filename.json` to create GeoJSON file with standardized field names.
