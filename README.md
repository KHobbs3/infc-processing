# infc-processing
Scripts to generate standardized GeoJSON files from various sources.

1. Place data files under appropriate `processing/input/region/municipality/`
2. Complete `generator/variablemap.csv`
3. Run `python jsongenerator.py` to create JSONs for each data source.
4. Run `python jsonprocessor.py ../generator/json/filename.json` to create GeoJSON file with standardized field names.
