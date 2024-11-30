import ipywidgets as ipw
from aiidalab_qe_vibroscopy.app.widgets.dielectricmodel import DielectricModel
from aiidalab_qe.common.widgets import LoadingWidget


class DielectricWidget(ipw.VBox):
    """
    Widget for displaying dielectric properties results
    """

    def __init__(self, model: DielectricModel, dielectric_node: None, **kwargs):
        super().__init__(
            children=[LoadingWidget("Loading widgets")],
            **kwargs,
        )
        self._model = model

    def render(self):
        if self.rendered:
            return

        self.dielectric_results_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            The DielectricWorkchain computes different properties: <br>
                <em style="display: inline-block; margin-left: 20px;">-High Freq. Dielectric Tensor </em> <br>
                <em style="display: inline-block; margin-left: 20px;">-Born Charges </em> <br>
                <em style="display: inline-block; margin-left: 20px;">-Raman Tensors </em> <br>
                <em style="display: inline-block; margin-left: 20px;">-The non-linear optical susceptibility tensor </em> <br>
                All information can be downloaded as a JSON file. <br>

            </div>"""
        )

        self.children = [
            self.dielectric_results_help,
        ]

        self.rendered = True
