"""Bands results view widgets"""

from __future__ import annotations


import numpy as np


from aiida_vibroscopy.utils.broadenings import multilorentz


def plot_powder(
    frequencies: list[float],
    intensities: list[float],
    broadening: float = 10.0,
    x_range: list[float] | str = "auto",
    broadening_function=multilorentz,
    normalize: bool = True,
):
    frequencies = np.array(frequencies)
    intensities = np.array(intensities)

    if x_range == "auto":
        xi = max(0, frequencies.min() - 200)
        xf = frequencies.max() + 200
        x_range = np.arange(xi, xf, 1.0)

    y_range = broadening_function(x_range, frequencies, intensities, broadening)

    if normalize:
        y_range /= y_range.max()

    return x_range, y_range


def export_iramanworkchain_data(node):
    """
    We have multiple choices: IR, RAMAN.
    """

    if "iraman" in node:
        output_node = node.iraman
    elif "harmonic" in node:
        output_node = node.harmonic
    else:
        # we have raman and ir only if we run IRamanWorkChain or HarmonicWorkChain
        return None

    if "vibrational_data" in output_node:
        # We enable the possibility to provide both spectra.
        # We give as output or string, or the output node.

        spectra_data = {
            "Raman": None,
            "Ir": None,
        }

        vibrational_data = output_node.vibrational_data
        vibro = (
            vibrational_data.numerical_accuracy_4
            if hasattr(vibrational_data, "numerical_accuracy_4")
            else vibrational_data.numerical_accuracy_2
        )

        if "born_charges" in vibro.get_arraynames():
            (
                polarized_intensities,
                frequencies,
                labels,
            ) = vibro.run_powder_ir_intensities()
            total_intensities = polarized_intensities

            # sometimes IR/Raman has not active peaks by symmetry, or due to the fact that 1st order cannot capture them
            if len(total_intensities) == 0:
                spectra_data["Ir"] = (
                    "No IR modes detected."  # explanation added in the main results script of the app.
                )
            else:
                spectra_data["Ir"] = output_node

        if "raman_tensors" in vibro.get_arraynames():
            (
                polarized_intensities,
                depolarized_intensities,
                frequencies,
                labels,
            ) = vibro.run_powder_raman_intensities(frequency_laser=532, temperature=300)
            total_intensities = polarized_intensities + depolarized_intensities

            # sometimes IR/Raman has not active peaks by symmetry, or due to the fact that 1st order cannot capture them
            if len(total_intensities) == 0:
                spectra_data["Raman"] = (
                    "No Raman modes detected."  # explanation added in the main results script of the app.
                )
            else:
                spectra_data["Raman"] = output_node

        return spectra_data
    else:
        return None
