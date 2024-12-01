import ipywidgets as ipw
from aiidalab_qe_vibroscopy.app.widgets.ramanmodel import RamanModel
import plotly.graph_objects as go
from aiidalab_widgets_base.utils import StatusHTML


class RamanWidget(ipw.VBox):
    """
    Widget to display Raman properties Tab
    """

    def __init__(self, model: RamanModel, node: None, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading Raman data...")],
            **kwargs,
        )
        self._model = model
        self._model.vibro = node
        self.rendered = False

    def render(self):
        if self.rendered:
            return

        self.raman_plot_type = ipw.ToggleButtons(
            description="Spectrum type:",
            style={"description_width": "initial"},
        )
        ipw.dlink(
            (self._model, "raman_plot_type_options"),
            (self.raman_plot_type, "options"),
        )
        ipw.link(
            (self._model, "raman_plot_type"),
            (self.raman_plot_type, "value"),
        )
        self.raman_plot_type.observe(self._on_raman_plot_type_change, names="value")
        self.raman_temperature = ipw.FloatText(
            description="Temperature (K):",
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "raman_temperature"),
            (self.raman_temperature, "value"),
        )
        self.raman_frequency_laser = ipw.FloatText(
            description="Laser frequency (nm):",
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "raman_frequency_laser"),
            (self.raman_frequency_laser, "value"),
        )
        self.raman_pol_incoming = ipw.Text(
            description="Incoming polarization:",
            style={"description_width": "initial"},
            layout=ipw.Layout(visibility="hidden"),
        )
        ipw.link(
            (self._model, "raman_pol_incoming"),
            (self.raman_pol_incoming, "value"),
        )
        self.raman_pol_outgoing = ipw.Text(
            description="Outgoing polarization:",
            style={"description_width": "initial"},
            layout=ipw.Layout(visibility="hidden"),
        )
        ipw.link(
            (self._model, "raman_pol_outgoing"),
            (self.raman_pol_outgoing, "value"),
        )
        self.raman_plot_button = ipw.Button(
            description="Update Plot",
            icon="pencil",
            button_style="primary",
            layout=ipw.Layout(width="auto"),
        )
        self.raman_plot_button.on_click(self._on_raman_plot_button_click)
        self.raman_download_button = ipw.Button(
            description="Download Data",
            icon="download",
            button_style="primary",
            layout=ipw.Layout(width="auto"),
        )
        self.raman_download_button.on_click(self._model.download_data)
        self._wrong_syntax = StatusHTML(clear_after=8)

        self.raman_broadening = ipw.FloatText(
            description="Broadening (cm-1):",
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "raman_broadening"),
            (self.raman_broadening, "value"),
        )

        self.raman_separate_polarized = ipw.Checkbox(
            description="Separate polarized and depolarized intensities",
            style={"description_width": "initial"},
        )
        ipw.link(
            (self._model, "raman_separate_polarizations"),
            (self.raman_separate_polarized, "value"),
        )
        self.raman_spectrum = go.FigureWidget(
            layout=go.Layout(
                title=dict(text="Powder Raman spectrum"),
                barmode="overlay",
                xaxis=dict(
                    title="Wavenumber (cm-1)",
                    nticks=0,
                ),
                yaxis=dict(
                    title="Intensity (arb. units)",
                ),
                height=500,
                width=700,
                plot_bgcolor="white",
            )
        )

        self.children = [
            ipw.HTML("<h3>Raman spectroscopy</h3>"),
            ipw.HTML(
                """<div style="line-height: 140%; padding-top: 10px; padding-bottom: 10px">
                Select the type of Raman spectrum to plot.
                </div>"""
            ),
            self.raman_plot_type,
            self.raman_temperature,
            self.raman_frequency_laser,
            self.raman_broadening,
            self.raman_separate_polarized,
            self.raman_pol_incoming,
            self.raman_pol_outgoing,
            ipw.HBox([self.raman_plot_button, self.raman_download_button]),
            self.raman_spectrum,
            ipw.HTML("<h3>IR spectroscopy</h3>"),
        ]

        self.rendered = True
        self._initial_view()

    def _initial_view(self):
        self._model.fetch_data()
        self._model.update_data()
        self.raman_spectrum.add_scatter(
            x=self._model.frequencies, y=self._model.intensities, name=""
        )

    def _on_raman_plot_type_change(self, change):
        if change["new"] == "single_crystal":
            self.raman_pol_incoming.layout.visibility = "visible"
            self.raman_pol_outgoing.layout.visibility = "visible"
            self.raman_separate_polarized.layout.visibility = "hidden"
        else:
            self.raman_pol_incoming.layout.visibility = "hidden"
            self.raman_pol_outgoing.layout.visibility = "hidden"
            self.raman_separate_polarized.layout.visibility = "visible"

    def _on_raman_plot_button_click(self, _):
        _, incoming_syntax_ok = self._model._check_inputs_correct(
            self.raman_pol_incoming.value
        )
        _, outgoing_syntax_ok = self._model._check_inputs_correct(
            self.raman_pol_outgoing.value
        )
        if not (incoming_syntax_ok and outgoing_syntax_ok):
            self._wrong_syntax.message = """
                <div class='alert alert-danger'>
                    ERROR: Invalid syntax for polarization directions.
                </div>
            """
            return
        self._model.update_data()
        self._model.update_plot(self.raman_spectrum)
