import ipywidgets as ipw
from aiidalab_qe_vibroscopy.app.widgets.euphonic.single_crystal_model import (
    SingleCrystalFullModel,
)
import plotly.graph_objects as go


class SingleCrystalFullWidget(ipw.VBox):
    def __init__(self, model: SingleCrystalFullModel, node: None, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading Single Crystal data...")],
            **kwargs,
        )
        self._model = model
        self._model.vibro = node
        self.rendered = False

    def render(self):
        if self.rendered:
            return

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

        self.fig = go.FigureWidget()

        self.slider_intensity = ipw.FloatRangeSlider(
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
        ipw.link(
            (self._model, "slider_intensity"),
            (self.slider_intensity, "value"),
        )

        self.E_units_button = ipw.ToggleButtons(
            description="Energy units:",
            layout=ipw.Layout(
                width="auto",
            ),
        )
        ipw.dlink(
            (self._model, "E_units_button_options"),
            (self.E_units_button, "options"),
        )

        ipw.link(
            (self._model, "E_units"),
            (self.E_units_button, "value"),
        )

        self.plot_button = ipw.Button(
            description="Replot",
            icon="pencil",
            button_style="primary",
            disabled=True,
            layout=ipw.Layout(width="auto"),
        )

        self.reset_button = ipw.Button(
            description="Reset",
            icon="recycle",
            button_style="primary",
            disabled=False,
            layout=ipw.Layout(width="auto"),
        )

        self.download_button = ipw.Button(
            description="Download Data and Plot",
            icon="download",
            button_style="primary",
            disabled=False,  # Large files...
            layout=ipw.Layout(width="auto"),
        )

        self.q_spacing = ipw.FloatText(
            step=0.001,
            description="q step (1/A)",
            tooltip="q spacing in 1/A",
        )
        ipw.link(
            (self._model, "q_spacing"),
            (self.q_spacing, "value"),
        )
        self.energy_broadening = ipw.FloatText(
            step=0.01,
            description="&Delta;E (meV)",
            tooltip="Energy broadening in meV",
        )
        ipw.link(
            (self._model, "energy_broadening"),
            (self.energy_broadening, "value"),
        )

        self.energy_bins = ipw.IntText(
            description="#E bins",
            tooltip="Number of energy bins",
        )
        ipw.link(
            (self._model, "energy_bins"),
            (self.energy_bins, "value"),
        )

        self.temperature = ipw.FloatText(
            step=0.01,
            description="T (K)",
            disabled=False,
        )
        ipw.link(
            (self._model, "temperature"),
            (self.temperature, "value"),
        )

        self.weight_button = ipw.ToggleButtons(
            options=[
                ("Coherent", "coherent"),
                ("DOS", "dos"),
            ],
            description="weight:",
            disabled=False,
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "weighting"),
            (self.weight_button, "value"),
        )

        self.custom_kpath = ipw.Text(
            description="Custom path (rlu):",
            style={"description_width": "initial"},
        )

        ipw.link(
            (self._model, "custom_kpath"),
            (self.custom_kpath, "value"),
        )

        self.children = [
            ipw.HTML("<h3>Neutron dynamic structure factor - Single Crystal</h3>"),
            self.fig,
            self.slider_intensity,
            ipw.HTML("(Intensity is relative to the maximum intensity at T=0K)"),
            self.E_units_button,
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
                            self.custom_kpath,
                        ],
                        layout=ipw.Layout(
                            width="70%",
                        ),
                    ),
                ],  # end of HBox children
            ),
        ]

        self.rendered = True
        self._init_view()

    def _init_view(self, _=None):
        print("Init view")
        # self._model._update_spectra()

    #     self._model.fetch_data()
    #     self._needs_single_crystal_widget()
    #     self.render_widgets()

    # def _needs_single_crystal_widget(self):
    #     if self._model.needs_single_crystal_tab:
    #         self.single_crystal_model = SingleCrystalModel()
    #         self.single_crystal_widget = SingleCrystalWidget(
    #             model=self.single_crystal_model,
    #             node=self._model.vibro,
    #         )
    #         self.children = (*self.children, self.single_crystal_widget)

    # def render_widgets(self):
    #     if self._model.needs_single_crystal_tab:
    #         self.single_crystal_widget.render()
