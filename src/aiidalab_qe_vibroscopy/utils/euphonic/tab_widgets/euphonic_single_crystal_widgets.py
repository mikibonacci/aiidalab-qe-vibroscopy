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
    StructureFactorSettingsBaseWidget,
    COLORSCALE,
    COLORBAR_DICT,
    StructureFactorBasePlotWidget,
)


class SingleCrystalPlotWidget(StructureFactorBasePlotWidget):
    def render(self):
        if self.rendered:
            return

        super().render()

        heatmap_trace = go.Heatmap(
            z=self._model.final_zspectra.T,
            y=self._model.y[:, 0] * self.THz_to_meV,
            x=None,
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
        self.fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=self._model.ticks_positions,
                ticktext=self._model.ticks_labels,
            )
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

        x = None  # if mode == "intensity" else x[0]
        self.fig.add_trace(
            go.Heatmap(
                z=self._model.final_zspectra.T,
                y=(
                    self._model.y[:, 0] * self.THz_to_meV
                    if self.E_units_button.value == "meV"
                    else self._model.y[:, 0]
                ),
                x=x,  # self._model.x,
                colorbar=COLORBAR_DICT,
                colorscale=COLORSCALE,  # imported from euphonic_base_widgets
            )
        )

        # change the path wants also a change in the labels.
        # this is delays things
        self.fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=self._model.ticks_positions,
                ticktext=self._model.ticks_labels,
            )
        )

        self.fig.data = [self.fig.data[1]]

        super()._update_plot()


class SingleCrystalSettingsWidget(StructureFactorSettingsBaseWidget):
    def render(self):
        if self.rendered:
            return

        super().render()

        self.custom_kpath_description = ipw.HTML(
            """
            <div style="padding-top: 0px; padding-bottom: 0px; line-height: 140%;">
                <b>Custom q-points path for the structure factor</b>: <br>
                we can provide it via a specific format: <br>
                (1) each linear path should be divided by '|'; <br>
                (2) each path is composed of 'qxi qyi qzi - qxf qyf qzf' where qxi and qxf are, respectively,
                the start and end x-coordinate of the q direction, in reciprocal lattice units (rlu).<br>
                An example path is: '0 0 0 - 1 1 1 | 1 1 1 - 0.5 0.5 0.5'. <br>
                For now, we do not support fractions (i.e. we accept 0.5 but not 1/2).
            </div>
            """
        )

        self.custom_kpath_text = ipw.Text(
            value="",
            description="Custom path (rlu):",
            style={"description_width": "initial"},
        )
        custom_style = '<style>.custom-font { font-family: "Monospaced"; font-size: 16px; }</style>'
        display(ipw.HTML(custom_style))
        self.custom_kpath_text.add_class("custom-font")
        ipw.link(
            (self._model, "custom_kpath"),
            (self.custom_kpath_text, "value"),
        )
        self.custom_kpath_text.observe(self._on_setting_changed, names="value")

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
                            self.energy_broadening,
                            self.energy_bins,
                            self.temperature,
                            self.weight_button,
                        ],
                        layout=ipw.Layout(
                            width="60%",
                        ),
                    ),
                    ipw.VBox(
                        [
                            self.custom_kpath_description,
                            self.custom_kpath_text,
                        ],
                        layout=ipw.Layout(
                            width="70%",
                        ),
                    ),
                ],  # end of HBox children
            ),
        ]


class SingleCrystalFullWidget(ipw.VBox):
    # I need to put the model also HERE! Think how we can so all of this in simpler way.
    """
    The Widget to display specifically the Intensity map of Dynamical structure
    factor for single crystal. It is composed of the following widgets:
    - title_intensity: HTML widget with the title of the widget.
    - settings_intensity: SingleCrystalSettingsWidget widget with the settings for the plot.
    - map_widget: SingleCrystalPlotWidget widget with the plot of the intensity map.
    - download_button: Button widget to download the intensity map.


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
            "<h3>Neutron dynamic structure factor - Single Crystal</h3>"
        )

        # we initialize and inject the model here.
        self.settings_intensity = SingleCrystalSettingsWidget(model=self._model)
        self.map_widget = SingleCrystalPlotWidget(model=self._model)

        # rendering the widgets
        self.settings_intensity.render()
        self.map_widget.render()

        # specific for the single crystal
        self.settings_intensity.plot_button.on_click(self._on_plot_button_clicked)
        self.settings_intensity.download_button.on_click(self.download_data)

        self.children = [
            self.title_intensity,
            self.map_widget,
            self.settings_intensity,
        ]

    def _on_plot_button_clicked(self, change=None):
        self.settings_intensity.plot_button.disabled = True
        self.map_widget._update_plot()

    def download_data(self, _=None):
        """
        Download both the ForceConstants and the spectra json files.
        TODO: improve the format, should be easy to open somewhere else.
        """
        force_constants_dict = self.fc.to_dict()

        filename = "single_crystal.json"
        my_dict = {}
        my_dict["x"] = self._model.final_xspectra.tolist()
        my_dict["y"] = self._model.y.tolist()
        my_dict["z"] = self._model.final_zspectra.tolist()
        my_dict.update(self._model.get_model_state())
        for k in ["weighting", "q_spacing", "temperature"]:
            filename += "_" + k + "_" + str(my_dict[k])

        # FC download:
        json_str = json.dumps(jsanitize(force_constants_dict))
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename="force_constants.json")

        # Powder data download:
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
