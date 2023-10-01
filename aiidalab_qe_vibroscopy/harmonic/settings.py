# -*- coding: utf-8 -*-
"""Panel for PhononWorkchain plugin.

Authors:

    * Miki Bonacci <miki.bonacci@psi.ch>
    Inspired by Xing Wang <xing.wang@psi.ch>
"""
import ipywidgets as ipw
from aiida.orm import Float, Int, Str

from aiidalab_qe.common.panel import Panel
from aiida_vibroscopy.common.properties import PhononProperty


class Setting(Panel):
    title = "Harmonic Settings"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_panel_value(self):
        """Return a dictionary with the input parameters for the plugin."""
        return 

    def load_panel_value(self, input_dict):
        """Load a dictionary with the input parameters for the plugin."""
        pass