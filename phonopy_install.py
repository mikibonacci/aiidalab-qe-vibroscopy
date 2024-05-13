from aiida.common.exceptions import NotExistent
import subprocess
from aiida.orm import load_code
from aiida import load_profile


def install_phonopy():
    load_profile()
    try:
        load_code("phonopy@localhost")
    except NotExistent:
        # Construct the command as a list of arguments
        command = [
            "verdi",
            "code",
            "create",
            "core.code.installed",
            "--non-interactive",
            "--label",
            "phonopy",
            "--default-calc-job-plugin",
            "phonopy.phonopy",
            "--computer",
            "localhost",
            "--filepath-executable",
            "/home/jovyan/.local/bin/phonopy",
        ]

        # Use subprocess.run to run the command
        subprocess.run(command, check=True)
    else:
        raise Warning("Code phonopy@localhost already installed!")


# Called when the script is run directly
if __name__ == "__main__":
    install_phonopy()
