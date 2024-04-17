# python file to convert ymls to ldes
import subprocess
import os
import yaml
from pyrdfj2 import J2RDFSyntaxBuilder
import pathlib

QUERYBUILDER = J2RDFSyntaxBuilder(
    templates_folder=pathlib.Path(__file__).parent / "templates"
)
CONFIG_LOCATION = pathlib.Path(__file__).parent / "../config.yml"

BASE_DIR = os.path.dirname(os.getcwd())

print(BASE_DIR)

loaded_config = yaml.safe_load(open(CONFIG_LOCATION, "r"))

# mkdir ldes folder if it doesn't exist
if not os.path.isdir(os.path.join(BASE_DIR, "ldes")):
    os.mkdir(os.path.join(BASE_DIR, "ldes"))

# use the config file to get the unique concepts
all_concepts = []
for source in loaded_config["sources"]:
    for item in source["items"]:
        all_concepts.append(item["path"])

all_concepts = set(all_concepts)
print(all_concepts)

ldes_fragment = QUERYBUILDER.build_syntax(
    "ldes_constraints.ttl",
    shacl_properties=all_concepts,
)

fname = "ldes_constraints.ttl"
with open(os.path.join(BASE_DIR, "ldes", fname), "w") as f:
    f.write(ldes_fragment)


def get_changed_files():

    # open .github/hash file and read the hash
    with open(os.path.join(BASE_DIR, ".github/last_ldes_hash"), "r") as f:
        hash = f.read()
    print(hash)

    # get current hash
    current_hash = subprocess.run(
        "git rev-parse HEAD".split(), capture_output=True, text=True
    ).stdout.strip()
    print(current_hash)

    # get the list of changed files
    changed_files = subprocess.run(
        f"git diff --name-only {hash} {current_hash}".split(),
        capture_output=True,
        text=True,
    ).stdout.strip()
    changed_files = changed_files.split("\n")
    return changed_files, hash, current_hash


changed_files, last_hash, current_hash = get_changed_files()
print(f"Changed files: {changed_files}")
print(f"Last hash: {last_hash}")
print(f"Current hash: {current_hash}")


mock_data = [
    ".github/workflows/pull_request.yml",
    "P02/http___vocab_nerc_ac_uk_collection_P02_current_ACSR_.yml",
    "P02/http___vocab_nerc_ac_uk_collection_P02_current_AASD_.yml",
    "P02/http___vocab_nerc_ac_uk_collection_P02_current_ALKY_.yml",
    "P02/http___vocab_nerc_ac_uk_collection_P02_current_ARAD_.yml",
    "P02/http___vocab_nerc_ac_uk_collection_P02_current_AATX_.yml",
    "src/poetry.lock",
    "src/pyproject.toml",
    "src/ymls_to_ldes_ttl.py",
]


# use the mock data to test the script
def make_ldes_ttl_file(changed_files, previous_hash, current_hash):
    # reduce the list of files to only the yml files or workflow file sin .github
    yml_files = [
        file
        for file in changed_files
        if file.endswith(".yml") and not file.startswith(".github")
    ]
    print(f"YML FILES: {yml_files}")
    all_files_dict = []
    for file in yml_files:
        try:
            print(f"File: {file}")
            parent_dir = os.path.join(BASE_DIR, file)
            print(f"Parent dir: {parent_dir}")
            loaded_file = yaml.safe_load(open(parent_dir, "r"))
            all_files_dict.append(loaded_file)
        except FileNotFoundError:
            print(f"File {file} not found")
            # !TODO: This is an edgecase that needs to be dealt with
    print(all_files_dict)

    # pre-prune the list of files so that only tranlations are included for the ones that have translations
    new_all_files_dict = []
    for file in all_files_dict:
        new_labels = []
        for label in file["labels"]:
            translation_found = False
            non_empty_translations = []
            for translation in label["translations"]:
                for key, value in translation.items():
                    if value != "":
                        non_empty_translations.append(translation)
                        translation_found = True
            label["translations"] = non_empty_translations
            new_labels.append(label)
            if translation_found:
                file["labels"] = new_labels
                new_all_files_dict.append(file)
                break

    print(new_all_files_dict)

    # make a ttl ldes fragment
    ldes_fragment = QUERYBUILDER.build_syntax(
        "ldes_feed.ttl",
        this_fragment_delta=current_hash,
        next_fragment_delta=previous_hash,
        retention_period=1,
        concepts=new_all_files_dict,
    )

    # write the ldes fragment to a file
    # fragment name is the current hash
    fname = f"{current_hash}.ttl"
    with open(os.path.join(BASE_DIR, "ldes", fname), "w") as f:
        f.write(ldes_fragment)

    # write the current hash to the last hash file
    with open(os.path.join(BASE_DIR, ".github/last_ldes_hash"), "w") as f:
        f.write(current_hash)


make_ldes_ttl_file(changed_files, last_hash, current_hash)
