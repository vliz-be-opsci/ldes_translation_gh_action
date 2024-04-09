# python file to convert ymls to ldes
import subprocess


def get_changed_files():
    command = "git branch -r"
    result = subprocess.run(command.split(), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return []
    return result.stdout.splitlines()


changed_files = get_changed_files()
print(changed_files)
