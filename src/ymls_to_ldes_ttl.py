# python file to convert ymls to ldes
import subprocess
import os
import yaml
from pyrdfj2 import J2RDFSyntaxBuilder
import pathlib

QUERYBUILDER = J2RDFSyntaxBuilder(
    templates_folder=pathlib.Path(__file__).parent / "templates"
)


def get_changed_files():

    # open .github/hash file and read the hash
    with open(os.path.join(os.getcwd(), ".github/last_ldes_hash"), "r") as f:
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
    return changed_files


changed_files = get_changed_files()
print(changed_files)
print(type(changed_files))


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
    all_files_dict = []
    for file in yml_files:
        try:
            parent_dir = os.path.join(os.getcwd(), os.path.abspath(file))
            loaded_file = yaml.safe_load(open(parent_dir, "r"))
            all_files_dict.append(loaded_file)
        except FileNotFoundError:
            print(f"File {file} not found")
            # !TODO: This is an edgecase that needs to be dealt with
    print(all_files_dict)

    # make a ttl ldes fragment
    ldes_fragment = QUERYBUILDER.build_syntax(
        "ldes_feed.ttl",
        this_fragment_delta=current_hash,
        next_fragment_delta=previous_hash,
        retention_period=1,
        concepts=all_files_dict,
    )

    # mkdir ldes folder if it doesn't exist
    if not os.path.isdir(os.path.join(os.getcwd(), "ldes")):
        os.mkdir(os.path.join(os.getcwd(), "ldes"))

    # write the ldes fragment to a file
    # fragment name is the current hash
    fname = f"{current_hash}.ttl"
    with open(os.path.join(os.getcwd(), "ldes", fname), "w") as f:
        f.write(ldes_fragment)


make_ldes_ttl_file(mock_data, "16768yu", "5674548HUBI")
