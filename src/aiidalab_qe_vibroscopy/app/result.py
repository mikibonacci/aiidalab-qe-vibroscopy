"""Bands results view widgets"""

from __future__ import annotations


from aiidalab_qe.common.panel import ResultPanel


from ..utils.euphonic import (
    export_euphonic_data,
    EuphonicSuperWidget,
)

import ipywidgets as ipw


class Result(ResultPanel):
    """
    The idea is that this Panel should be divided in sub panels,
    one for each section of properties: phonons, spectroscopies, inelastic neutron scattering.
    """

    title = "Vibrational Structure"
    workchain_label = "vibro"
    children_result_widget = ()

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, identifier="vibro", **kwargs)
        self._update_view()

    def _update_view(self):
        children_result_widget = ()
        tab_titles = []  # this is needed to name the sub panels

        ins_data = export_euphonic_data(self.node)

        # euphonic
        if ins_data:
            intensity_maps = EuphonicSuperWidget(
                fc=ins_data["fc"], q_path=ins_data["q_path"]
            )
            children_result_widget += (intensity_maps,)
            tab_titles.append("Inelastic Neutrons")

        self.result_tabs = ipw.Tab(children=children_result_widget)

        for title_index in range(len(tab_titles)):
            self.result_tabs.set_title(title_index, tab_titles[title_index])

        self.children = [self.result_tabs]
