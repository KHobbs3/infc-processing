# infc-processing
Scripts to produce standardized JSON files from several data sources.

## Generator

1. Manually complete `generator/variablemap.csv`.
2. Run json generator script to create JSONs for each data source.

## Processor
1. Place data files under appropriate `processing/input/region/municipality/`.
	* region folder is labelled "00-PP" where 00 is the 2-digit Standard Geographical Code code and PP is the 2-letter Alpha code. For more information see [Table D](https://www.statcan.gc.ca/en/subjects/standard/sgc/2016/introduction#a4.1).
	* municipality subfolder is named in title case with no spaces between text.
2. Run json processing scipt to create JSON output files for each source with:
	* standardized field names
	* columns not mentioned in schema dropped
	* data filtered according to `separate` values
	* fixed `source_url`, `licence`, `municipality`, `prov/terr`, `provider`, `class` fields appended

## Usage
	> python jsongenerator.py
	> python jsonprocessor.py ../generator/json/filename.json
	
To process all data sources at once...

	> ./run_all.sh
