# -*- coding: utf-8 -*-
"""Panel for PhononWorkchain plugin.

Authors:

    * Miki Bonacci <miki.bonacci@psi.ch>
    Inspired by Xing Wang <xing.wang@psi.ch>
"""
import ipywidgets as ipw
from aiida.orm import Float, Int, Str

from aiidalab_qe.panel import Panel
from aiida_vibroscopy.common.properties import PhononProperty


class Setting(Panel):
    title = "Dielectric Settings"

    def __init__(self, **kwargs):
        self.settings_title = ipw.HTML(
            """<div style="padding-top: 0px; padding-bottom: 0px">
            <h4>Dielectric settings</h4></div>"""
        )
        self.settings_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            Please set the dielectric property to be computed in the simulation.
            If you want only a phonon calculation, just select <b>none</b>.
            </div>"""
        )
        self.workchain_protocol = ipw.ToggleButtons(
            options=["fast", "moderate", "precise"],
            value="moderate",
        )

        self.dielectric_property = ipw.Dropdown(
            options=[
                'dielectric',
                'ir', 
                'raman', 
                'born-charges', 
                'nac', 
                'bec', 
                'susceptibility-derivative',
                'non-linear-susceptibility',
                'none'
                ],
            value="dielectric",
            description="Desired dielectric property:",
            disabled=False,
            style={"description_width": "initial"},
        )

        self.children = [
            self.settings_title,
            self.settings_help,
            self.dielectric_property,

        ]
        super().__init__(**kwargs)

    def get_panel_value(self):
        """Return a dictionary with the input parameters for the plugin."""
        return {
            "dielectric": {
                "dielectric_property":{
                    self.dielectric_property.value,
                },
            },
        }

    def load_panel_value(self, input_dict):
        """Load a dictionary with the input parameters for the plugin."""
        self.dielectric_property.value = input_dict.get("dielectric_property", "dielectric")
