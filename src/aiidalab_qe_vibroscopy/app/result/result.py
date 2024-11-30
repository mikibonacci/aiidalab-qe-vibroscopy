"""Vibronic results view widgets"""

from aiidalab_qe_vibroscopy.app.result.model import VibroResultsModel
from aiidalab_qe.common.panel import ResultsPanel

import ipywidgets as ipw


class VibroResultsPanel(ResultsPanel[VibroResultsModel]):
    title = "Vibronic"
    identifier = "vibronic"
    workchain_labels = ["vibro"]

    def render(self):
        if self.rendered:
            return

        self.tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )

        tab_data = []
        # vibro_node = self._model.get_vibro_node()

        if self._model.needs_phonons_tab():
            tab_data.append(("Phonons", ipw.HTML("phonon_data")))

        if self._model.needs_raman_tab():
            tab_data.append(("Raman", ipw.HTML("raman_data")))

        if self._model.needs_dielectric_tab():
            tab_data.append(("Dielectric", ipw.HTML("dielectric_data")))

        if self._model.needs_euphonic_tab():
            tab_data.append(("Euphonic", ipw.HTML("euphonic_data")))

        # Assign children and titles dynamically
        self.tabs.children = [content for _, content in tab_data]

        for index, (title, _) in enumerate(tab_data):
            self.tabs.set_title(index, title)

        self.children = [self.tabs]
        self.rendered = True
