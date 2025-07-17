"""AiiDAlab Qe plugin for vibrational spectoscopy."""

import os
import sys


# Disable
def blockPrint():
    """Disable print output."""
    sys.stdout = open(os.devnull, "w")


# Restore
def enablePrint():
    """Enable print output."""
    sys.stdout = sys.__stdout__


has_mace = False
try:
    blockPrint()  # Suppress output during import
    # it is very quick import
    from mace import build  # noqa: F401

    enablePrint()  # Restore output
    has_mace = True
except ImportError:
    enablePrint()
    # MACE is not installed, skipping MACE-related functionality.
