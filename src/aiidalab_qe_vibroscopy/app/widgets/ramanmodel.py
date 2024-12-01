from __future__ import annotations
from aiidalab_qe.common.mvc import Model
import traitlets as tl
from aiida.common.extendeddicts import AttributeDict
from IPython.display import display
import numpy as np
from aiida_vibroscopy.utils.broadenings import multilorentz
import plotly.graph_objects as go
import base64
import json


class RamanModel(Model):
    vibro = tl.Instance(AttributeDict, allow_none=True)

    raman_plot_type_options = tl.List(
        trait=tl.List(tl.Unicode()),
        default_value=[
            ("Powder", "powder"),
            ("Single Crystal", "single_crystal"),
        ],
    )
    raman_plot_type = tl.Unicode("powder")
    raman_temperature = tl.Float(300)
    raman_frequency_laser = tl.Float(532)
    raman_pol_incoming = tl.Unicode("0 0 1")
    raman_pol_outgoing = tl.Unicode("0 0 1")
    raman_broadening = tl.Float(10.0)
    raman_separate_polarizations = tl.Bool(False)

    frequencies = []
    intensities = []

    frequencies_depolarized = []
    intensities_depolarized = []

    def fetch_data(self):
        """Fetch the Raman data from the VibroWorkChain"""
        self.raman_data = self.get_vibrational_data(self.vibro)

    def update_data(self):
        """
        Update the Raman plot data based on the selected plot type and configuration.
        """
        if self.raman_plot_type == "powder":
            self._update_powder_data()
        else:
            self._update_single_crystal_data()

    def _update_powder_data(self):
        """
        Update data for the powder Raman plot.
        """
        (
            polarized_intensities,
            depolarized_intensities,
            frequencies,
            _,
        ) = self.raman_data.run_powder_raman_intensities(
            frequencies=self.raman_frequency_laser,
            temperature=self.raman_temperature,
        )

        if self.raman_separate_polarizations:
            self.frequencies, self.intensities = self.generate_plot_data(
                frequencies,
                polarized_intensities,
                self.raman_broadening,
            )
            self.frequencies_depolarized, self.intensities_depolarized = (
                self.generate_plot_data(
                    frequencies,
                    depolarized_intensities,
                    self.raman_broadening,
                )
            )
        else:
            combined_intensities = polarized_intensities + depolarized_intensities
            self.frequencies, self.intensities = self.generate_plot_data(
                frequencies,
                combined_intensities,
                self.raman_broadening,
            )
            self.frequencies_depolarized, self.intensities_depolarized = [], []

    def _update_single_crystal_data(self):
        """
        Update data for the single crystal Raman plot.
        """
        dir_incoming, _ = self._check_inputs_correct(self.raman_pol_incoming)
        dir_outgoing, _ = self._check_inputs_correct(self.raman_pol_outgoing)

        (
            intensities,
            frequencies,
            labels,
        ) = self.raman_data.run_single_crystal_raman_intensities(
            pol_incoming=dir_incoming,
            pol_outgoing=dir_outgoing,
            frequencies=self.raman_frequency_laser,
            temperature=self.raman_temperature,
        )
        self.frequencies, self.intensities = self.generate_plot_data(
            frequencies, intensities
        )
        self.frequencies_depolarized, self.intensities_depolarized = [], []

    def update_plot(self, plot):
        """
        Update the Raman plot based on the selected plot type and configuration.

        Parameters:
            plot: The plotly.graph_objs.Figure widget to update.
        """
        update_function = (
            self._update_powder_plot
            if self.raman_plot_type == "powder"
            else self._update_single_crystal_plot
        )
        update_function(plot)

    def _update_powder_plot(self, plot):
        """
        Update the powder Raman plot.

        Parameters:
            plot: The plotly.graph_objs.Figure widget to update.
        """
        if self.raman_separate_polarizations:
            self._update_polarized_and_depolarized(plot)
        else:
            self._clear_depolarized_and_update(plot)

    def _update_polarized_and_depolarized(self, plot):
        """
        Update the plot when polarized and depolarized data are separate.

        Parameters:
            plot: The plotly.graph_objs.Figure widget to update.
        """
        if len(plot.data) == 1:
            self._update_trace(
                plot.data[0], self.frequencies, self.intensities, "Polarized"
            )
            plot.add_trace(
                go.Scatter(
                    x=self.frequencies_depolarized,
                    y=self.intensities_depolarized,
                    name="Depolarized",
                )
            )
            plot.layout.title.text = "Powder Raman Spectrum"
        elif len(plot.data) == 2:
            self._update_trace(
                plot.data[0], self.frequencies, self.intensities, "Polarized"
            )
            self._update_trace(
                plot.data[1],
                self.frequencies_depolarized,
                self.intensities_depolarized,
                "Depolarized",
            )
            plot.layout.title.text = "Powder Raman Spectrum"

    def _clear_depolarized_and_update(self, plot):
        """
        Clear depolarized data and update the plot.

        Parameters:
            plot: The plotly.graph_objs.Figure widget to update.
        """
        if len(plot.data) == 2:
            self._update_trace(plot.data[0], self.frequencies, self.intensities, "")
            plot.data[1].x = []
            plot.data[1].y = []
            plot.layout.title.text = "Powder Raman Spectrum"
        elif len(plot.data) == 1:
            self._update_trace(plot.data[0], self.frequencies, self.intensities, "")
            plot.layout.title.text = "Powder Raman Spectrum"

    def _update_single_crystal_plot(self, plot):
        """
        Update the single crystal Raman plot.

        Parameters:
            plot: The plotly.graph_objs.Figure widget to update.
        """
        if len(plot.data) == 2:
            self._update_trace(plot.data[0], self.frequencies, self.intensities, "")
            plot.data[1].x = []
            plot.data[1].y = []
            plot.layout.title.text = "Single Crystal Raman Spectrum"
        elif len(plot.data) == 1:
            self._update_trace(plot.data[0], self.frequencies, self.intensities, "")
            plot.layout.title.text = "Single Crystal Raman Spectrum"

    def _update_trace(self, trace, x_data, y_data, name):
        """
        Helper function to update a single trace in the plot.

        Parameters:
            trace: The trace to update.
            x_data: The new x-axis data.
            y_data: The new y-axis data.
            name: The name of the trace.
        """
        trace.x = x_data
        trace.y = y_data
        trace.name = name

    def get_vibrational_data(self, node):
        """
        Extract vibrational data from an IRamanWorkChain or HarmonicWorkChain node.

        Parameters:
            node: The workchain node containing IRaman or Harmonic data.

        Returns:
            The vibrational accuracy data (vibro) or None if not available.
        """
        # Determine the output node
        output_node = getattr(node, "iraman", None) or getattr(node, "harmonic", None)
        if not output_node:
            return None

        # Check for vibrational data and extract accuracy
        vibrational_data = getattr(output_node, "vibrational_data", None)
        if not vibrational_data:
            return None

        # Extract vibrational accuracy (prefer numerical_accuracy_4 if available)
        vibro = getattr(vibrational_data, "numerical_accuracy_4", None) or getattr(
            vibrational_data, "numerical_accuracy_2", None
        )

        return vibro

    def _check_inputs_correct(self, polarization):
        # Check if the polarization vectors are correct
        input_text = polarization
        input_values = input_text.split()
        dir_values = []
        if len(input_values) == 3:
            try:
                dir_values = [float(i) for i in input_values]
                return dir_values, True
            except:  # noqa: E722
                return dir_values, False
        else:
            return dir_values, False

    def generate_plot_data(
        self,
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

    def download_data(self, _=None):
        filename = "spectra.json"
        if self.raman_separate_polarizations:
            my_dict = {
                "Frequencies cm-1": self.frequencies.tolist(),
                "Polarized intensities": self.intensities.tolist(),
                "Depolarized intensities": self.intensities_depolarized.tolist(),
            }
        else:
            my_dict = {
                "Frequencies cm-1": self.frequencies.tolist(),
                "Intensities": self.intensities.tolist(),
            }
        json_str = json.dumps(my_dict)
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename=filename)

    @staticmethod
    def _download(payload, filename):
        from IPython.display import Javascript

        javas = Javascript(
            """
            var link = document.createElement('a');
            link.href = 'data:text/json;charset=utf-8;base64,{payload}'
            link.download = "{filename}"
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """.format(payload=payload, filename=filename)
        )
        display(javas)
