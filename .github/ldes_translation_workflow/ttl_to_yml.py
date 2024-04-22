# this file will convert a given ttl file with the config.yml file to a series of small editable yml files

import os
import pathlib
from config_validation import load_config
from pyrdfj2 import J2RDFSyntaxBuilder
import rdflib
import re
import json

CONFIG_LOCATION = pathlib.Path(__file__).parent.parent / "../config.yml"
QUERYBUILDER = J2RDFSyntaxBuilder(
    templates_folder=pathlib.Path(__file__).parent / "templates"
)

config = load_config(CONFIG_LOCATION)

languages_to_fill = config["target_languages"]

for source in config["sources"]:
    source_name = source["name"]
    source_path_ttl = (
        pathlib.Path(__file__).parent.parent
        / f"../{source_name}"
        / "output_ldes_stream.ttl"
    )

    # Preprocess the ttl file to replace spaces with 'T' in datetime strings -> required for rdflib otherwise it throws an error
    with open(source_path_ttl, "r") as f:
        data = f.read()
    data = re.sub(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d)", r"\1T\2", data)
    with open(source_path_ttl, "w") as f:
        f.write(data)

    # load in the ttl file with rdflib
    g = rdflib.Graph()
    g.parse(source_path_ttl, format="ttl")

    # get all the variables needed to form the quert from the config file
    source_id_path = source["id-path"]
    source_language = source["language"]
    source_items = source["items"]

    # create the sparql query
    sparql_query = QUERYBUILDER.build_syntax(
        "query.sparql",
        language=source_language,
        id_path=source_id_path,
        dict_key_values=source_items,
    )

    print(sparql_query)

    # perform the query
    qres = g.query(sparql_query)

    # convert the qres to a json object
    json_res = qres.serialize(format="json")
    # load the json object into a python object
    json_res = json.loads(json_res)
    for row in json_res["results"]["bindings"]:
        # print(row)
        # print(languages_to_fill)
        # print(source_language)
        # print(source_items)

        yml_text = QUERYBUILDER.build_syntax(
            "single_yml.yml",
            row=row,
            languages=languages_to_fill,
            source_items=source_items,
        )

        identifier_raw = row["id_node"]["value"]

        # process id so that it is a valid file name
        identifier = re.sub(r"[^a-zA-Z0-9]", "_", identifier_raw)

        # print(yml_text)
        # write the ouput to a file
        # location file is ../{source_name}/row["identifier"]["value"].yml

        with open(
            pathlib.Path(__file__).parent.parent / f"../{source_name}/{identifier}.yml",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(yml_text)
