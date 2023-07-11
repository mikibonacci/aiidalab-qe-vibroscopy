from aiidalab_qe_vibroscopy.harmonic.settings import Setting
from aiidalab_qe_vibroscopy.harmonic.workchain import workchain_and_builder
#from aiidalab_qe_eos.phonons.result import Result
from aiidalab_qe.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "Phononic and Dielectric properties"
    #description = "Select to proceed with the calculation of the phononic and dielectric properties"

property ={
"setting": Setting,
"workchain": workchain_and_builder,
#"result": Result,
}