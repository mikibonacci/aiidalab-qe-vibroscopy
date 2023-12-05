from aiida.common.exceptions import NotExistent
import subprocess
from aiida.orm import load_code
from aiida import load_profile


def install_phonopy():
    load_profile()
    try:
        load_code("phonopy2@localhost")
    except NotExistent:
        # Construct the command as a list of arguments
        command = [
            "verdi",
            "code",
            "create",
            "core.code.installed",
            "--non-interactive",
            "--label",
            "phonopy2",
            "--default-calc-job-plugin",
            "phonopy.phonopy",
            "--computer",
            "localhost",
            "--filepath-executable",
            "/opt/conda/bin/phonopy",
        ]

        # Use subprocess.run to run the command
        subprocess.run(command, check=True)


# Called when the script is run directly
if __name__ == "__main__":
    install_phonopy()
