"""Bands results view widgets"""

from __future__ import annotations


import ipywidgets as ipw
import numpy as np
from IPython.display import HTML, clear_output, display

from weas_widget import WeasWidget

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


class ActiveModesWidget(ipw.VBox):
    """Widget that display an animation (nglview) of the active modes."""

    def __init__(self, node, output_node, spectrum_type, **kwargs):
        self.node = node
        self.output_node = output_node
        self.spectrum_type = spectrum_type

        # WeasWidget configuration
        self.guiConfig = {
            "enabled": True,
            "components": {
                "atomsControl": True,
                "buttons": True,
                "cameraControls": True,
            },
            "buttons": {
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }
        # VibrationalData
        vibrational_data = self.output_node.vibrational_data
        self.vibro = (
            vibrational_data.numerical_accuracy_4
            if hasattr(vibrational_data, "numerical_accuracy_4")
            else vibrational_data.numerical_accuracy_2
        )

        # Raman or IR active modes
        selection_rule = self.spectrum_type.lower()
        frequencies, self.eigenvectors, self.labels = self.vibro.run_active_modes(
            selection_rule=selection_rule,
        )
        self.rounded_frequencies = [round(frequency, 3) for frequency in frequencies]

        # StructureData
        self.structure_ase = self.node.inputs.structure.get_ase()

        modes_values = [
            f"{index + 1}: {value}"
            for index, value in enumerate(self.rounded_frequencies)
        ]
        # Create Raman modes widget
        self.active_modes = ipw.Dropdown(
            options=modes_values,
            value=modes_values[0],  # Default value
            description="Select mode:",
            style={"description_width": "initial"},
        )

        self.amplitude = ipw.FloatText(
            value=3.0,
            description="Amplitude :",
            disabled=False,
            style={"description_width": "initial"},
        )

        self._supercell = [
            ipw.BoundedIntText(value=1, min=1, layout={"width": "40px"}),
            ipw.BoundedIntText(value=1, min=1, layout={"width": "40px"}),
            ipw.BoundedIntText(value=1, min=1, layout={"width": "40px"}),
        ]

        self.supercell_selector = ipw.HBox(
            [
                ipw.HTML(
                    description="Super cell:", style={"description_width": "initial"}
                )
            ]
            + self._supercell
        )

        self.modes_table = ipw.Output()
        self.animation = ipw.Output()
        self._display_table()
        self._select_active_mode(None)
        widget_list = [
            self.active_modes,
            self.amplitude,
            self._supercell[0],
            self._supercell[1],
            self._supercell[2],
        ]
        for elem in widget_list:
            elem.observe(self._select_active_mode, names="value")

        super().__init__(
            children=[
                ipw.HBox(
                    [
                        ipw.VBox(
                            [
                                ipw.HTML(
                                    value=f"<b> {self.spectrum_type} Active Modes </b>"
                                ),
                                self.modes_table,
                            ]
                        ),
                        ipw.VBox(
                            [
                                self.active_modes,
                                self.amplitude,
                                self.supercell_selector,
                                self.animation,
                            ],
                            layout={"justify_content": "center"},
                        ),
                    ]
                ),
            ]
        )

    def _display_table(self):
        """Display table with the active modes."""
        # Create an HTML table with the active modes
        table_data = [list(x) for x in zip(self.rounded_frequencies, self.labels)]
        table_html = "<table>"
        table_html += "<tr><th>Frequencies (cm-1) </th><th> Label</th></tr>"
        for row in table_data:
            table_html += "<tr>"
            for cell in row:
                table_html += "<td style='text-align:center;'>{}</td>".format(cell)
            table_html += "</tr>"
        table_html += "</table>"
        # Set layout to a fix size
        self.modes_table.layout = {
            "overflow": "auto",
            "height": "200px",
            "width": "150px",
        }
        with self.modes_table:
            clear_output()
            display(HTML(table_html))

    def _select_active_mode(self, change):
        """Display animation of the selected active mode."""
        self._animation_widget()
        with self.animation:
            clear_output()
            display(self.weas)

    def _animation_widget(self):
        """Create animation widget."""
        # Get the index of the selected mode
        index_str = self.active_modes.value.split(":")[0]
        index = int(index_str) - 1
        # Get the eigenvector of the selected mode
        eigenvector = self.eigenvectors[index]
        # Get the amplitude of the selected mode
        amplitude = self.amplitude.value
        # Get the structure of the selected mode
        structure = self.structure_ase

        self.weas = WeasWidget(guiConfig=self.guiConfig)
        self.weas.from_ase(structure)

        phonon_setting = {
            "eigenvectors": np.array(
                [[[real_part, 0] for real_part in row] for row in eigenvector]
            ),
            "kpoint": [0, 0, 0],  # optional
            "amplitude": amplitude,
            "factor": amplitude * 0.6,
            "nframes": 20,
            "repeat": [
                self._supercell[0].value,
                self._supercell[1].value,
                self._supercell[2].value,
            ],
            "color": "black",
            "radius": 0.1,
        }
        self.weas.avr.phonon_setting = phonon_setting

        self.weas.avr.model_style = 1
        self.weas.avr.color_type = "JMOL"
        self.weas.avr.vf.show = True
