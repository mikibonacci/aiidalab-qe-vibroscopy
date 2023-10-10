from aiidalab_qe_vibroscopy.workflows.settings import Setting
from aiidalab_qe_vibroscopy.workflows.workchain import workchain_and_builder
from aiidalab_qe_vibroscopy.workflows.result import Result
from aiidalab_qe.common.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "Vibrational properties"
    #description = "IR and Raman spectra; you may also select phononic and dielectric properties"

property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
"result": Result,
}