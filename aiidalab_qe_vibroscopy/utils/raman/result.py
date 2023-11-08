"""Bands results view widgets

"""
from __future__ import annotations


from widget_bandsplot import BandsPlotWidget

from aiidalab_qe.common.panel import ResultPanel
import ipywidgets as ipw
import numpy as np
from IPython.display import clear_output, display
import base64
import json


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

class SpectrumPlotWidget(ipw.VBox):
    """Widget that allows different options for plotting Raman Spectrum."""

    description = ipw.HTML(
        """<div style="line-height: 140%; padding-top: 10px; padding-bottom: 10px">
        Select the type of Raman spectrum to plot.
        </div>"""
    )
    def __init__(self, node, **kwargs):
        self.node = node
        #VibriationalData 
        self.vibro = self.node.outputs.vibronic.iraman.vibrational_data.numerical_accuracy_4
        self._plot_type = ipw.ToggleButtons(
            options=[
                ("Powder", "powder"),
                ("Single Crystal", "single_crystal"),
            ],
            value="powder",
            description="Spectrum type:",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.temperature = ipw.FloatText(
            value=298.0,
            description="Temperature (K):",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.frequency_laser = ipw.FloatText(
            value=532.0,
            description="Laser frequency (nm):",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.pol_incoming = ipw.Text(
            value="0 0 1",
            description="Incoming polarization:",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.pol_outgoing = ipw.Text(
            value="0 0 1",
            description="Outgoing polarization:",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.plot_button = ipw.Button(
            description="Plot",
            icon="pencil",
            button_style="primary",
            disabled=False,
            layout=ipw.Layout(width="auto"),
        )
        self.download_button = ipw.Button(
            description="Download Data",
            icon="download",
            button_style="primary",
            disabled=False,
            layout=ipw.Layout(width="auto", visibility="hidden"),
        )
        self.wrong_syntax = ipw.HTML(
            value="""<i class="fa fa-times" style="color:red;font-size:2em;" ></i> wrong syntax""",
            layout={"visibility": "hidden"},
        )
        self.spectrum_widget = ipw.Output()
        self.frequencies = []
        self.intensities = []
        self.polarization_out = ipw.Output()
        
        def download_data(_=None):
            filename = "spectra.json"
            my_dict = {"Frequencies cm-1": self.frequencies.tolist(), "Intensities": self.intensities.tolist()}
            json_str = json.dumps(my_dict)
            b64_str = base64.b64encode(json_str.encode()).decode()
            self._download(payload=b64_str, filename=filename)


        self._plot_type.observe(self._on_plot_type_change, names="value")
        self.plot_button.on_click(self._on_plot_button_clicked)
        self.download_button.on_click(download_data)
        super().__init__(
            children=[
                self.description,
                self._plot_type,
                self.temperature,
                self.frequency_laser,
                self.polarization_out,
                ipw.HBox([self.plot_button, self.download_button]),
                self.wrong_syntax,
                self.spectrum_widget,
            ]
        )

    @staticmethod
    def _download(payload, filename):
        from IPython.display import Javascript

        javas = Javascript(
            """
            var link = document.createElement('a');
            link.href = 'data:text/json;charset=utf-8;base64,{payload}'
            link.download = "{filename}"
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """.format(
                payload=payload, filename=filename
            )
        )
        display(javas)

    def _on_plot_type_change(self, change):
        if change["new"] == "single_crystal":
            with self.polarization_out:
                clear_output()
                display(self.pol_incoming)
                display(self.pol_outgoing)
        else:
            self.pol_incoming.value = "0 0 1"
            self.pol_outgoing.value = "0 0 1"
            self.wrong_syntax.layout.visibility = "hidden"
            with self.polarization_out:
                clear_output()

    def _on_plot_button_clicked(self, change):
        if self._plot_type.value == "powder":
            # Powder spectrum
            polarized_intensities, depolarized_intensities, frequencies, labels = self.vibro.run_powder_raman_intensities(frequencies=self.frequency_laser.value, temperature=self.temperature.value)
            total_intensities =  polarized_intensities + depolarized_intensities
            self.frequencies , self.intensities = plot_powder(frequencies, total_intensities)
            self._display_figure()
            
            
        else:
            # Single crystal spectrum
            dir_incoming, correct_syntax_incoming = self._check_inputs_correct(self.pol_incoming)
            dir_outgoing, correct_syntax_outgoing = self._check_inputs_correct(self.pol_outgoing)
            if not correct_syntax_incoming or not correct_syntax_outgoing:
                self.wrong_syntax.layout.visibility = "visible"
                return
            else:
                self.wrong_syntax.layout.visibility = "hidden"
                intensities, frequencies, labels = self.vibro.run_single_crystal_raman_intensities(pol_incoming=dir_incoming, pol_outgoing=dir_incoming, frequencies=self.frequency_laser.value, temperature=self.temperature.value)
                self.frequencies , self.intensities = plot_powder(frequencies, intensities)
                self._display_figure()

    def _check_inputs_correct(self,polarization):
        #Check if the polarization vectors are correct
        input_text = polarization.value
        input_values = input_text.split()
        dir_values = []
        if len(input_values) == 3:
            try:
                dir_values = [float(i) for i in input_values]
                return dir_values, True
            except:
                return dir_values, False
        else:
            return dir_values, False

    def _spectrum_widget(self):
        import plotly.graph_objects as go

        fig = go.FigureWidget(
            layout=go.Layout(
                title=dict(text="Raman spectrum"),
                barmode="overlay",
            )
        )
        fig.layout.xaxis.title = "Wavenumber (cm-1)"
        fig.layout.yaxis.title = "Intensity (arb. units)"
        fig.layout.xaxis.nticks = 0 
        fig.add_scatter(x=self.frequencies,y=self.intensities,name=f"")
        fig.update_layout(
            height=500,
            width=700,
            plot_bgcolor="white",


        )
        return fig

    def _display_figure(self):
        with self.spectrum_widget:
                    clear_output()
                    display(self._spectrum_widget())
                    self.download_button.layout.visibility = "visible"
        
        
  




