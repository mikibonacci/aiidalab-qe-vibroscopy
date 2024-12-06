import base64
from IPython.display import display


import ipywidgets as ipw
import plotly.graph_objects as go
import plotly.io as pio

# from ..euphonic.bands_pdos import *

import json
from monty.json import jsanitize

# sys and os used to prevent euphonic to print in the stdout.

from aiidalab_qe_vibroscopy.utils.euphonic.base_widgets.euphonic_base_widgets import (
    StructureFactorBasePlotWidget,
    StructureFactorSettingsBaseWidget,
    COLORBAR_DICT,
    COLORSCALE,
)


class PowderPlotWidget(StructureFactorBasePlotWidget):
    def render(self):
        if self.rendered:
            return

        super().render()

        heatmap_trace = go.Heatmap(
            z=self._model.final_zspectra.T,
            y=self._model.y[:, 0] * self.THz_to_meV,
            x=self._model.x[0],
            colorbar=COLORBAR_DICT,
            colorscale=COLORSCALE,  # imported from euphonic_base_widgets
        )

        # Add colorbar
        colorbar = heatmap_trace.colorbar
        colorbar.x = 1.05  # Move colorbar to the right
        colorbar.y = 0.5  # Center colorbar vertically

        # Add heatmap trace to figure
        self.fig.add_trace(heatmap_trace)

        # Layout settings
        self.fig["layout"]["xaxis"].update(
            title="|q| (1/A)",
            range=[min(self._model.final_xspectra), max(self._model.final_xspectra)],
        )
        self.fig["layout"]["yaxis"].update(
            title="meV",
            range=[min(self._model.y[:, 0]), max(self._model.y[:, 0])],
        )

        if self.fig.layout.images:
            for image in self.fig.layout.images:
                image["scl"] = 2  # Set the scale for each image

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

    def _update_plot(self):
        # update the spectra, i.e. the data contained in the _model.
        self._model._update_spectra()

        self.fig.add_trace(
            go.Heatmap(
                z=self._model.final_zspectra.T,
                y=(
                    self._model.y[:, 0] * self.THz_to_meV
                    if self.E_units_button.value == "meV"
                    else self._model.y[:, 0]
                ),
                x=self._model.x[0],
                colorbar=COLORBAR_DICT,
                colorscale=COLORSCALE,  # imported from euphonic_base_widgets
            )
        )

        self.fig.data = [self.fig.data[1]]

        super()._update_plot()


class PowderSettingsWidget(StructureFactorSettingsBaseWidget):
    def render(self):
        if self.rendered:
            return

        super().render()

        self.qmin = ipw.FloatText(
            value=0,
            description="|q|<sub>min</sub> (1/A)",
        )
        ipw.link(
            (self._model, "q_min"),
            (self.qmin, "value"),
        )
        self.qmin.observe(self._on_setting_changed, names="value")

        self.qmax = ipw.FloatText(
            step=0.01,
            value=1,
            description="|q|<sub>max</sub> (1/A)",
        )
        ipw.link(
            (self._model, "q_max"),
            (self.qmax, "value"),
        )
        self.qmax.observe(self._on_setting_changed, names="value")

        self.int_npts = ipw.IntText(
            value=100,
            description="npts",
            tooltip="Number of points to be used in the average sphere.",
        )
        ipw.link(
            (self._model, "npts"),
            (self.int_npts, "value"),
        )
        self.int_npts.observe(self._on_setting_changed, names="value")

        # Please note: if you change the order of the widgets below, it will
        # affect the usage of the children[0] below in the full widget.

        self.children = [
            ipw.HBox(
                [
                    ipw.VBox(
                        [
                            ipw.HBox(
                                [
                                    self.reset_button,
                                    self.plot_button,
                                    self.download_button,
                                ]
                            ),
                            self.q_spacing,
                            self.qmin,
                            self.qmax,
                            # self.int_npts,
                        ],
                        layout=ipw.Layout(
                            width="50%",
                        ),
                    ),
                    ipw.VBox(
                        [
                            self.energy_broadening,
                            self.energy_bins,
                            self.temperature,
                            self.weight_button,
                        ],
                        layout=ipw.Layout(
                            width="50%",
                        ),
                    ),
                ],  # end of HBox children
            ),
        ]


class PowderFullWidget(ipw.VBox):
    """
    The Widget to display specifically the Intensity map of Dynamical structure
    factor for powder samples.

    The scattering lengths used in the `produce_bands_weigthed_data` function
    are tabulated (Euphonic/euphonic/data/sears-1992.json)
    and are from Sears (1992) Neutron News 3(3) pp26--37.
    """

    def __init__(self, model):
        self._model = model
        self.rendered = False
        super().__init__()

    def render(self):
        if self.rendered:
            return

        self.title_intensity = ipw.HTML(
            "<h3>Neutron dynamic structure factor - Powder sample</h3>"
        )

        # we initialize and inject the model here.
        self.settings_intensity = PowderSettingsWidget(model=self._model)
        self.map_widget = PowderPlotWidget(model=self._model)

        # rendering the widgets
        self.settings_intensity.render()
        self.map_widget.render()

        # specific for the powder
        self.settings_intensity.plot_button.on_click(self._on_plot_button_clicked)
        self.settings_intensity.download_button.on_click(self.download_data)

        super().__init__(
            children=[
                self.title_intensity,
                self.map_widget,
                self.settings_intensity,
            ],
        )

        self.rendered = True

    def _on_plot_button_clicked(self, change=None):
        self.settings_intensity.plot_button.disabled = True
        self.map_widget._update_plot()

    def download_data(self, _=None):
        """
        Download both the ForceConstants and the spectra json files.
        """
        force_constants_dict = self.fc.to_dict()

        filename = "powder"
        my_dict = self.spectra.to_dict()
        my_dict.update(self._model.get_model_state())
        for k in ["weighting", "q_spacing", "temperature"]:
            filename += "_" + k + "_" + str(my_dict[k])

        # FC download:
        json_str = json.dumps(jsanitize(force_constants_dict))
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename="force_constants.json")

        # Powder download:
        json_str = json.dumps(jsanitize(my_dict))
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename=filename + ".json")

        # Plot download:
        ## Convert the FigureWidget to an image in base64 format
        image_bytes = pio.to_image(
            self.map_widget.children[1], format="png", width=800, height=600
        )
        b64_str = base64.b64encode(image_bytes).decode()
        self._download(payload=b64_str, filename=filename + ".png")

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
