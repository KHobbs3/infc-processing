#!/bin/bash
FILES="../generator/json/*.json"
for f in $FILES
do
  echo "Processing $f..."
  python jsonprocessor.py $f
done
