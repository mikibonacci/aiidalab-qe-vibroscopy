from aiidalab_qe.common.panel import ResultsModel
import traitlets as tl


class VibroResultsModel(ResultsModel):
    identifier = "vibronic"

    _this_process_label = "VibroWorkChain"

    tab_titles = tl.List([])

    def get_vibro_node(self):
        return self._get_child_outputs()
