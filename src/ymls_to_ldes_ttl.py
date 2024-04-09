# python file to convert ymls to ldes
import subprocess
import os


def get_changed_files():
    # Get the names of the source and base branches from the GitHub context
    source_branch = os.getenv("GITHUB_HEAD_REF")
    base_branch = os.getenv("GITHUB_BASE_REF")

    # Fetch the base branch from the remote repository
    fetch_command = f"git fetch origin {base_branch}:{base_branch}"
    subprocess.run(fetch_command.split(), capture_output=True, text=True)

    # Compare differences between the source and base branches
    diff_command = f"git diff --name-only {base_branch} {source_branch}"
    result = subprocess.run(diff_command.split(), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return []
    return result.stdout.splitlines()


changed_files = get_changed_files()
print(changed_files)
