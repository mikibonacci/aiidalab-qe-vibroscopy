from aiidalab_qe_vibroscopy.raman.settings import Setting
from aiidalab_qe_vibroscopy.raman.workchain import workchain_and_builder
#from aiidalab_qe_eos.raman.result import Result
from aiidalab_qe.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "Powder Raman spectrum"
    #description = "IR and Raman spectra; you may also select phononic and dielectric properties"

property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
#"result": Result,
}