from aiidalab_qe.common.panel import ResultsModel
import traitlets as tl


from aiidalab_qe_vibroscopy.utils.raman.result import export_iramanworkchain_data
from aiidalab_qe_vibroscopy.utils.phonons.result import export_phononworkchain_data
from aiidalab_qe_vibroscopy.utils.euphonic import export_euphonic_data


class VibroResultsModel(ResultsModel):
    identifier = "vibronic"

    _this_process_label = "VibroWorkChain"

    tab_titles = tl.List([])

    def get_vibro_node(self):
        return self._get_child_outputs()

    def needs_dielectric_tab(self):
        node = self.get_vibro_node()
        if not any(key in node for key in ["iraman", "dielectric", "harmonic"]):
            return False
        return True

    def needs_raman_tab(self):
        return export_iramanworkchain_data(self.get_vibro_node())

    # Here we use _fetch_child_process_node() since the function needs the input_structure in inputs
    def needs_phonons_tab(self):
        return export_phononworkchain_data(self._fetch_child_process_node())

    # Here we use _fetch_child_process_node() since the function needs the input_structure in inputs
    def needs_euphonic_tab(self):
        return export_euphonic_data(self._fetch_child_process_node())
