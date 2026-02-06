#! /bin/bash

rm djtpms.zip; cd custom_components/djtpms && zip -r ../../djtpms.zip .; cd ../..; unzip -l djtpms.zip
