"""Vibronic results view widgets"""

from aiidalab_qe_vibroscopy.app.result.model import VibroResultsModel
from aiidalab_qe.common.panel import ResultsPanel


class VibroResultsPanel(ResultsPanel[VibroResultsModel]):
    title = "Vibronic"
    identifier = "vibronic"
    workchain_labels = ["vibro"]

    def render(self):
        if self.rendered:
            return
