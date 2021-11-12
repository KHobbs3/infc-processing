# infc-processing
Scripts to generate standardized GeoJSON files from various sources.

1. Place data files under appropriate `processing/input/region/municipality/`.
	* region folder is labelled "00-PP" where 00 is the 2-digit Standard Geographical Code code and PP is the 2-letter Alpha code. For more information see [Table D](https://www.statcan.gc.ca/en/subjects/standard/sgc/2016/introduction#a4.1).
	* municipality is named in title case with no spaces between text.
2. Manually complete `generator/variablemap.csv`.
3. Run `python jsongenerator.py` to create JSONs for each data source.
4. Run `python jsonprocessor.py ../generator/json/filename.json` to create JSON output files for each source with:
	* standardized field names
	* columns not mentioned in schema dropped
	* data filtered according to `separate` values
	* fixed source url, licence url, municipality, province/territory, provider, and class fields appended
