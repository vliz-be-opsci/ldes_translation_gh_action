#!/bin/bash

# check if there is a ../.././github/ldes folder in the repository, if not create it

if [ ! -d "../../ldes" ]; then
    mkdir "../../ldes"
    # run the ldes_download.sh script
    bash ldes_download.sh
    # run the ttl to yml python script
    poetry run python ttl_to_yml.py
fi