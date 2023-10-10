"""Bands results view widgets

"""
from __future__ import annotations


from widget_bandsplot import BandsPlotWidget

from aiidalab_qe.common.panel import ResultPanel

import numpy as np

from aiida_vibroscopy.utils.broadenings import multilorentz
def plot_powder(
    frequencies: list[float],
    intensities: list[float],
    broadening: float = 10.0,
    x_range: list[float] | str = 'auto',
    broadening_function=multilorentz,
    normalize: bool = True,):
    
    frequencies = np.array(frequencies)
    intensities = np.array(intensities)

    if x_range == 'auto':
        xi = max(0, frequencies.min() - 200)
        xf = frequencies.max() + 200
        x_range = np.arange(xi, xf, 1.)

    y_range = broadening_function(x_range, frequencies, intensities, broadening)

    if normalize:
        y_range /= y_range.max()

    return x_range, y_range
    
    
def export_iramanworkchain_data(node):

    '''
    We have multiple choices: IR, RAMAN.
    '''


    import json

    from monty.json import jsanitize

    parameters={}
    
    if not "vibronic" in node.outputs:
        return None
    else:
        if not "iraman" in node.outputs.vibronic:
            return None

    if "vibrational_data" in node.outputs.vibronic.iraman:
        
        vibro = node.outputs.vibronic.iraman.vibrational_data.numerical_accuracy_4
        
        try:
            #if node.inputs.iraman.dielectric.property == "ir":
            polarized_intensities, frequencies, labels = vibro.run_powder_ir_intensities(frequency_laser=532, temperature=300)
            total_intensities =  polarized_intensities 
            frequencies, total_intensities = plot_powder(frequencies, total_intensities)

            return [
                total_intensities,frequencies,labels,'Infrared vibrational spectrum'
            ]
        except:
            #elif node.inputs.iraman.dielectric.property == "raman":
            polarized_intensities, depolarized_intensities, frequencies, labels = vibro.run_powder_raman_intensities(frequency_laser=532, temperature=300)
            total_intensities =  polarized_intensities + depolarized_intensities
            frequencies, total_intensities = plot_powder(frequencies, total_intensities)
            return [
                total_intensities,frequencies,labels,'Raman vibrational spectrum'
            ]
  
    else:
        return None


class Result(ResultPanel):

    title = "Vibrational spectrum"
    workchain_label = "iraman"

    def _update_view(self):
        bands_data = export_iramanworkchain_data(self.node)

        if bands_data[3] in ["Raman vibrational spectrum","Infrared vibrational spectrum"]:
            import plotly.graph_objects as go

            frequencies = bands_data[1]
            total_intensities = bands_data[0]
            
            g = go.FigureWidget(
                layout=go.Layout(
                    title=dict(text=bands_data[3]),
                    barmode="overlay",
                )
            )
            g.layout.xaxis.title = "Wavenumber (cm-1)"
            g.layout.yaxis.title = "Intensity (arb. units)"
            g.layout.xaxis.nticks = 0 
            g.add_scatter(x=frequencies,y=total_intensities,name=f"")

            
            self.children = [
                g,
                ]





