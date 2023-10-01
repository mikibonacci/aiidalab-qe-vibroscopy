# -*- coding: utf-8 -*-
"""Setting Panel for PhononWorkchain plugin.

Authors:

    * Miki Bonacci <miki.bonacci@psi.ch>
    Inspired by Xing Wang <xing.wang@psi.ch>
"""
import ipywidgets as ipw

from aiidalab_qe.common.panel import Panel
from aiida_vibroscopy.common.properties import PhononProperty


class Setting(Panel):
    title = "Phonons Settings"

    def __init__(self, **kwargs):
        self.settings_title = ipw.HTML(
            """<div style="padding-top: 0px; padding-bottom: 0px">
            <h4>Frozen phonons settings</h4></div>"""
        )
        self.settings_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            Please select the phonon property to be computed in the simulation.
            </div>"""
        )
        self.workchain_protocol = ipw.ToggleButtons(
            options=["fast", "moderate", "precise"],
            value="moderate",
        )

        self.phonon_property = ipw.Dropdown(
            options=[
                ["bands","BANDS"], 
                ["dos","DOS"], 
                ["thermodynamic","THERMODYNAMIC"],
                ["force constants","NONE"],
            ],
            value="BANDS",
            description="Phonon property:",
            disabled=False,
            style={"description_width": "initial"},
        )

        self.children = [
            self.settings_title,
            self.settings_help,
            self.phonon_property,  
        ]
        super().__init__(**kwargs)

    def get_panel_value(self):
        """Return a dictionary with the input parameters for the plugin."""
        if isinstance(self.phonon_property,str):
            return {
            "phonon_property": self.phonon_property,
            }
        else:
            return {
                "phonon_property": self.phonon_property.value,
            }

    def load_panel_value(self, input_dict):
        """Load a dictionary with the input parameters for the plugin."""
        self.phonon_property.value = input_dict.get("phonon_property", "BANDS")
