import numpy as np
import traitlets as tl
import copy
import json
import base64
import plotly.io as pio
from monty.json import jsanitize
from IPython.display import display

from aiidalab_qe_vibroscopy.utils.euphonic.data_manipulation.intensity_maps import (
    AttrDict,
    produce_bands_weigthed_data,
    produce_powder_data,
    generated_curated_data,
    par_dict,
    par_dict_powder,
    export_euphonic_data,
)

from aiidalab_qe_vibroscopy.utils.euphonic.tab_widgets.euphonic_q_planes_widgets import (
    produce_Q_section_modes,
    produce_Q_section_spectrum,
)

from aiidalab_qe.common.mvc import Model


class EuphonicBaseResultsModel(Model):
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

    # Settings for single crystal and powder average
    q_spacing = tl.Float(0.01)
    energy_broadening = tl.Float(0.05)
    energy_bins = tl.Int(200)
    temperature = tl.Float(0)
    weighting = tl.Unicode("coherent")

    def fetch_data(self):
        """Fetch the data from the database or from the uploaded files."""
        # 1. from aiida, so we have the node
        if self.node:
            ins_data = export_euphonic_data(self.node)
            self.fc = ins_data["fc"]
            self.q_path = ins_data["q_path"]
        # 2. from uploaded files...
        else:
            self.fc = self.upload_widget._read_phonopy_files(
                fname=self.fname,
                phonopy_yaml_content=self._model.phonopy_yaml_content,
                fc_hdf5_content=self._model.fc_hdf5_content,
            )

    def _inject_single_crystal_settings(
        self,
    ):
        self.parameters = copy.deepcopy(
            par_dict
        )  # need to be different if powder or q section.
        self._callback_spectra_generation = produce_bands_weigthed_data
        # Dynamically add a trait for single crystal settings
        self.add_traits(custom_kpath=tl.Unicode(""))

    def _inject_powder_settings(
        self,
    ):
        self.parameters = copy.deepcopy(par_dict_powder)
        self._callback_spectra_generation = produce_powder_data
        # Dynamically add a trait for powder settings
        self.add_traits(q_min=tl.Float(0.0))
        self.add_traits(q_max=tl.Float(1))
        self.add_traits(npts=tl.Int(100))

    def _inject_qsection_settings(
        self,
    ):
        # self._callback_spectra_generation = produce_Q_section_modes
        # Dynamically add a trait for q section settings
        self.add_traits(center_e=tl.Float(0.0))
        self.add_traits(Q0_vec=tl.List(trait=tl.Float(), default_value=[0.0, 0.0, 0.0]))
        self.add_traits(
            h_vec=tl.List(trait=tl.Float(), default_value=[1, 1, 1, 100, 1])
        )
        self.add_traits(
            k_vec=tl.List(trait=tl.Float(), default_value=[1, 1, 1, 100, 1])
        )

    def set_model_state(self, parameters: dict):
        for k, v in parameters.items():
            setattr(self, k, v)

    def _get_default(self, trait):
        if trait in ["h_vec", "k_vec"]:
            return [1, 1, 1, 100, 1]
        elif trait == "Q0_vec":
            return [0.0, 0.0, 0.0]
        return self.traits()[trait].default_value

    def get_model_state(self):
        return {trait: getattr(self, trait) for trait in self.traits()}

    def reset(
        self,
    ):
        with self.hold_trait_notifications():
            for trait in self.traits():
                setattr(self, trait, self._get_default(trait))

    def _update_spectra(
        self,
    ):
        # This is used to update the spectra when the parameters are changed
        # and the
        if not hasattr(self, "parameters"):
            self._inject_single_crystal_settings()

        self.parameters.update(self.get_model_state())
        parameters_ = AttrDict(self.parameters)

        # custom linear path
        custom_kpath = self.custom_kpath if hasattr(self, "custom_kpath") else ""
        if len(custom_kpath) > 1:
            coordinates, labels = self.curate_path_and_labels()
            qpath = {
                "coordinates": coordinates,
                "labels": labels,  # ["$\Gamma$","X","X","(1,1,1)"],
                "delta_q": parameters_["q_spacing"],
            }
        else:
            qpath = copy.deepcopy(self.q_path)
            if qpath:
                qpath["delta_q"] = parameters_["q_spacing"]

        spectra, parameters = self._callback_spectra_generation(
            params=parameters_,
            fc=self.fc,
            linear_path=qpath,
            plot=False,
        )

        # curated spectra (labels and so on...)
        if hasattr(self, "custom_kpath"):  # single crystal case
            self.x, self.y = np.meshgrid(
                spectra[0].x_data.magnitude, spectra[0].y_data.magnitude
            )
            (
                self.final_xspectra,
                self.final_zspectra,
                self.ticks_positions,
                self.ticks_labels,
            ) = generated_curated_data(spectra)
        else:
            # Spectrum2D as output of the powder data
            self.x, self.y = np.meshgrid(
                spectra.x_data.magnitude, spectra.y_data.magnitude
            )

            # we don't need to curate the powder data,
            # we can directly use them:
            self.final_xspectra = spectra.x_data.magnitude
            self.final_zspectra = spectra.z_data.magnitude

    def _update_qsection_spectra(
        self,
    ):
        parameters_ = AttrDict(
            {
                "h": np.array([i for i in self.h_vec[:-2]]),
                "k": np.array([i for i in self.k_vec[:-2]]),
                "n_h": int(self.h_vec[-2]),
                "n_k": int(self.k_vec[-2]),
                "h_extension": self.h_vec[-1],
                "k_extension": self.k_vec[-1],
                "Q0": np.array([i for i in self.Q0_vec[:]]),
                "ecenter": self.center_e,
                "deltaE": self.energy_broadening,
                "bins": self.energy_bins,
                "spectrum_type": self.weighting,
                "temperature": self.temperature,
            }
        )

        modes, q_array, h_array, k_array, labels, dw = produce_Q_section_modes(
            self.fc,
            h=parameters_.h,
            k=parameters_.k,
            Q0=parameters_.Q0,
            n_h=parameters_.n_h,
            n_k=parameters_.n_k,
            h_extension=parameters_.h_extension,
            k_extension=parameters_.k_extension,
            temperature=parameters_.temperature,
        )

        self.av_spec, self.q_array, self.h_array, self.k_array, self.labels = (
            produce_Q_section_spectrum(
                modes,
                q_array,
                h_array,
                k_array,
                ecenter=parameters_.ecenter,
                deltaE=parameters_.deltaE,
                bins=parameters_.bins,
                spectrum_type=parameters_.spectrum_type,
                dw=dw,
                labels=labels,
            )
        )

    def curate_path_and_labels(
        self,
    ):
        # This is used to curate the path and labels of the spectra if custom kpath is provided.
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

    def _clone(self):
        return copy.deepcopy(self)

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
