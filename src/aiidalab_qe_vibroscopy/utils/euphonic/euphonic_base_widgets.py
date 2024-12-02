from IPython.display import display

import numpy as np
import ipywidgets as ipw

# from ..euphonic.bands_pdos import *
from .intensity_maps import *  # noqa: F403

# sys and os used to prevent euphonic to print in the stdout.

########################
################################ START DESCRIPTION
########################

"""
In this module we have the functions and widgets to be used in the app.
Essentially we create the force constants (fc) instance via the phonopy.yaml.

def export_phononworkchain_data(node, fermi_energy=None):
Functions from intensity_maps.py and bands_pdos.py are used in order to computed the quantities, in the
export_phononworkchain_data function, used then in the result.py panel.
"""

########################
################################ END DESCRIPTION
########################

COLORSCALE = "Viridis"
COLORBAR_DICT = dict(orientation="v", showticklabels=False, x=1, thickness=10, len=0.4)


# # Intensity map widget
class StructureFactorBasePlotWidget(ipw.VBox):
    """
    Widget to plot the Structure Factor for single crystals or powder samples.
    It takes as input the spectra as generated via the
    `produce_bands_weigthed_data` or `produce_powder_data` functions, called in the
    __init__ of the master widgets, respectively: `SingleCrystalFullWidget` and `PowderFullWidget`.

    NB: Intensity is relative to the maximum intensity at T=0K.

    We use this as base for three sub widgets: intensity, powder and q-sections.
    """

    THz_to_meV = 4.13566553853599  # conversion factor.

    def __init__(self, model, **kwargs):
        """

        Args:
            final_xspectra (_type_):
        """

        self._model = model
        
        final_xspectra = self._model.spectra
        
        self.message_fig = ipw.HTML("")
        self.message_fig.layout.display = "none"

        if self.fig.layout.images:
            for image in self.fig.layout.images:
                image["scl"] = 2  # Set the scale for each image

        self.fig["layout"]["xaxis"].update(
            range=[min(final_xspectra), max(final_xspectra)]
        )

        self.fig["layout"]["yaxis"].update(title="meV")

        self.fig.update_layout(
            height=500,
            width=700,
            margin=dict(l=15, r=15, t=15, b=15),
        )
        # Update x-axis and y-axis to enable autoscaling
        self.fig.update_xaxes(autorange=True)
        self.fig.update_yaxes(autorange=True)

        # Update the layout to enable autoscaling
        self.fig.update_layout(autosize=True)

        self.slider_intensity = ipw.FloatRangeSlider(
            value=[1, 100],  # Default selected interval
            min=1,
            max=100,
            step=1,
            orientation="horizontal",
            readout=True,
            readout_format=".0f",
            layout=ipw.Layout(
                width="400px",
            ),
        )
        self.slider_intensity.observe(self._update_intensity_filter, "value")

        self.specification_intensity = ipw.HTML(
            "(Intensity is relative to the maximum intensity at T=0K)"
        )

        self.E_units_button = ipw.ToggleButtons(
            options=[
                ("meV", "meV"),
                ("THz", "THz"),
                # ("cm<sup>-1</sup>", "cm-1"),
            ],
            value="meV",
            description="Energy units:",
            disabled=False,
            layout=ipw.Layout(
                width="auto",
            ),
        )
        self.E_units_button.observe(self._update_energy_units, "value")

        # Create and show figure
        super().__init__(
            children=[
                self.message_fig,
                self.fig,
                ipw.HBox([ipw.HTML("Intensity window (%):"), self.slider_intensity]),
                self.specification_intensity,
                self.E_units_button,
            ],
            layout=ipw.Layout(
                width="100%",
            ),
        )

    def _update_plot( # actually, should be an _update_plot... we don't modify data...
        self,
    ):
        # this will be called in the _update_plot method of SingleCrystalPlotWidget and PowderPlotWidget

        # Update the layout to enable autoscaling
        self.fig.update_layout(autosize=True)

        # We should do a check, if we have few points (<200?) provide like a warning..
        # Also decise less than what, 30%, 50%...?

        """
        visible_points = len(
            np.where(self.fig.data[0].z > 0.5)[0]
        )
        if visible_points < 1000:
            message = f"Only {visible_points}/{len(final_zspectra.T)} points have intensity higher than 50%"
            self.message_fig.value = message
            self.message_fig.layout.display = "block"
        else:
            self.message_fig.layout.display = "none"
        """

        # I have also to update the energy window. or better, to set the intensity to respect the current intensity window selected:
        self.fig.data[0].zmax = (
            self.slider_intensity.value[1] * np.max(self.fig.data[0].z) / 100
        )  # above this, it is all yellow, i.e. max intensity.
        self.fig.data[0].zmin = (
            self.slider_intensity.value[0] * np.max(self.fig.data[0].z) / 100
        )  # above this, it is all yellow, i.e. max intensity.

    def _update_intensity_filter(self, change):
        # the value of the intensity slider is in fractions of the max.
        if change["new"] != change["old"]:
            self.fig.data[0].zmax = (
                change["new"][1] * np.max(self.fig.data[0].z) / 100
            )  # above this, it is all yellow, i.e. max intensity.
            self.fig.data[0].zmin = (
                change["new"][0] * np.max(self.fig.data[0].z) / 100
            )  # below this, it is all blue, i.e. zero intensity

    def _update_energy_units(self, change):
        # the value of the intensity slider is in fractions of the max.
        if change["new"] != change["old"]:
            self.fig.data[0].y = (
                self.fig.data[0].y * self.THz_to_meV
                if change["new"] == "meV"
                else self.fig.data[0].y / self.THz_to_meV
            )

        self.fig["layout"]["yaxis"].update(title=change["new"])


#### SETTINGS WIDGET:


class StructureFactorSettingsBaseWidget(ipw.VBox):
    """
    Collects all the button and widget used to define settings for Neutron dynamic structure factor,
    both single crystal or powder.
    """

    def __init__(self, model, **kwargs):
        super().__init__()

        self._model = model
        
        self.q_spacing = ipw.FloatText(
            value=self._model.q_spacing,
            step=0.001,
            description="q step (1/A)",
            tooltip="q spacing in 1/A",
        )
        ipw.link(
            (self._model, "q_spacing"),
            (self.q_spacing, "value"),
        )
        self.q_spacing.observe(self._on_setting_changed, names="value")

        self.energy_broadening = ipw.FloatText(
            value=self._model.energy_broadening,
            step=0.01,
            description="&Delta;E (meV)",
            tooltip="Energy broadening in meV",
        )
        ipw.link(
            (self._model, "energy_broadening"),
            (self.energy_broadening, "value"),
        )
        self.energy_broadening.observe(self._on_setting_changed, names="value")

        self.energy_bins = ipw.IntText(
            value=self._model.energy_bins,
            description="#E bins",
            tooltip="Number of energy bins",
        )
        ipw.link(
            (self._model, "energy_bins"),
            (self.energy_bins, "value"),
        )
        self.energy_bins.observe(self._on_setting_changed, names="value")

        self.temperature = ipw.FloatText(
            value=self._model.temperature,
            step=0.01,
            description="T (K)",
            disabled=False,
        )
        ipw.link(
            (self._model, "temperature"),
            (self.temperature, "value"),
        )
        self.temperature.observe(self._on_setting_changed, names="value")

        self.weight_button = ipw.ToggleButtons(
            options=[
                ("Coherent", "coherent"),
                ("DOS", "dos"),
            ],
            value=self._model.weighting,
            description="weight:",
            disabled=False,
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "weighting"),
            (self.weight_button, "value"),
        )
        self.weight_button.observe(self._on_weight_button_change, names="value")

        self.plot_button = ipw.Button(
            description="Replot",
            icon="pencil",
            button_style="primary",
            disabled=True,
            layout=ipw.Layout(width="auto"),
        )
        self.plot_button.observe(self._on_plot_button_changed, names="disabled")

        self.reset_button = ipw.Button(
            description="Reset",
            icon="recycle",
            button_style="primary",
            disabled=False,
            layout=ipw.Layout(width="auto"),
        )
        self.reset_button.on_click(self._reset_settings)

        self.download_button = ipw.Button(
            description="Download Data and Plot",
            icon="download",
            button_style="primary",
            disabled=False,  # Large files...
            layout=ipw.Layout(width="auto"),
        )  

    def _on_plot_button_changed(self, change):
        if change["new"] != change["old"]:
            self.download_button.disabled = not change["new"]

    def _on_weight_button_change(self, change):
        if change["new"] != change["old"]:
            self.temperature.value = 0
            self.temperature.disabled = True if change["new"] == "dos" else False
            self.plot_button.disabled = False

    def _on_setting_changed(self, change): # think if we want to do something more evident... 
        self.plot_button.disabled = False
        
    def _reset_settings(self, _):
        self._model.reset()