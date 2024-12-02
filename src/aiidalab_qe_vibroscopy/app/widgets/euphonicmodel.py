import numpy as np
import traitlets as tl

from aiidalab_qe_vibroscopy.utils.euphonic.intensity_maps import (
    AttrDict,
    produce_bands_weigthed_data,
    generated_curated_data,
)

from aiidalab_qe.common.panel import ResultsModel

class EuphonicBaseResultsModel(ResultsModel):
    """Model for the neutron scattering results panel."""
    
    # Here we mode all the model and data-controller, i.e. all the data and their
    # manipulation to produce new spectra.
    # plot-controller, i.e. scales, colors and so on, should be attached to the widget, I think.
    # the above last point should be discussed more.
    
    # For now, we do only the first of the following:
    # 1. single crystal data: sc
    # 2. powder average: pa
    # 3. Q planes: qp
    # TRY it on the detached app.
    
    # AAA TOBE defined with respect to the type
    spectra = {}
    path = []
    q_path = None
    
    # check the SingleCrystalSettingsWidget and base
    q_spacing = tl.Float(0.01)
    energy_broadening = tl.Float(0.05)
    energy_bins = tl.Int(200)
    temperature = tl.Float(0)
    weighting = tl.Unicode("coherent")
    custom_kpath = tl.Unicode("")
    
    def fetch_data(self):
        """Fetch the data from the database."""
        # 1. from aiida, so we have the node
        # 2. from uploaded files...
        pass
        
    def set_model_state(self, parameters: dict):
        self.q_spacing = parameters.get("q_spacing", 0.01)
        self.energy_broadening = parameters.get("energy_broadening", 0.05)
        self.energy_bins = parameters.get("energy_bins", 200)
        self.temperature = parameters.get("temperature", 0)
        self.weighting = parameters.get("weighting", "coherent")
        self.custom_kpath = parameters.get("custom_kpath", "")
    
    def _get_default(self, trait):
        return self._defaults.get(trait, self.traits()[trait].default_value)
       
    def get_model_state(self):
        return {
            "q_spacing": self.q_spacing,
            "energy_broadening": self.energy_broadening,
            "energy_bins": self.energy_bins,
            "temperature": self.temperature,
            "weighting": self.weighting,
            "custom_kpath": self.custom_kpath,
        }
        
    def reset(self,):
        with self.hold_trait_notifications():
            self.q_spacing = 0.01
            self.energy_broadening = 0.5
            self.energy_bins = 200
            self.temperature = 0
            self.weight_button = "coherent"
            self.custom_kpath = ""
        
        
    def _update_spectra(self,):
        # can't do directly the following, as we want to have also detached app.
        #if not (process_node := self.fetch_process_node()):
        #    return
        
        # AAA
        # here I should generate the spectra with respect to the data I have, 
        # i.e. the FC and the parameters.
        # I need to fetch the FC if are not there, but I suppose are already there. 
        # the spectrum is initialized in the full sc widget.
        
        spectra, parameters = produce_bands_weigthed_data(
                    params=self.get_model_state(),
                    fc=self.fc,
                    linear_path=self.q_path,
                    plot=False,  # CHANGED
                )
        
        self.x, self.y = np.meshgrid(spectra[0].x_data.magnitude, spectra[0].y_data.magnitude)
        
        # This is used in order to have an overall intensity scale.
        self.intensity_ref_0K = np.max(spectra[0].z_data.magnitude)  # CHANGED

        # curated spectra (labels and so on...)
        (
            self.final_xspectra,
            self.final_zspectra,
            self.ticks_positions,
            self.ticks_labels,
        ) = generated_curated_data(spectra)
        
    
    def curate_path_and_labels(
        self,
    ):
        # I do not like this implementation (MB)
        coordinates = []
        labels = []
        path = self.custom_kpath
        linear_paths = path.split("|")
        for i in linear_paths:
            scoords = []
            s = i.split(
                " - "
            )  # not i.split("-"), otherwise also the minus of the negative numbers are used for the splitting.
            for k in s:
                labels.append(k.strip())
                # AAA missing support for fractions.
                l = tuple(map(float, [kk for kk in k.strip().split(" ")]))  # noqa: E741
                scoords.append(l)
            coordinates.append(scoords)
        return coordinates, labels
    
    def download_data(self, _=None):
        """
        Download both the ForceConstants and the spectra json files.
        """
        force_constants_dict = self.fc.to_dict()

        filename = "single_crystal.json"
        my_dict = {}
        for branch in range(len(self.spectra)):
            my_dict[str(branch)] = self.spectra[branch].to_dict()
        my_dict.update(
            {
                "weighting": self.weighting,
                "q_spacing": self.q_spacing,
                "energy_broadening": self.energy_broadening,
                "ebins": self.energy_bins,
                "temperature": self.temperature,
            }
        )
        for k in ["weighting", "q_spacing", "temperature"]:
            filename += "_" + k + "_" + str(my_dict[k])

        # FC download:
        json_str = json.dumps(jsanitize(force_constants_dict))
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename="force_constants.json")

        # Powder data download:
        json_str = json.dumps(jsanitize(my_dict))
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename=filename + ".json")

        # Plot download:
        ## Convert the FigureWidget to an image in base64 format
        image_bytes = pio.to_image(
            self.map_widget.children[1], format="png", width=800, height=600
        )
        b64_str = base64.b64encode(image_bytes).decode()
        self._download(payload=b64_str, filename=filename + ".png")

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
            """.format(payload=payload, filename=filename)
        )
        display(javas)