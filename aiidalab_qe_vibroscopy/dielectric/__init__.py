from aiidalab_qe_vibroscopy.dielectric.settings import Setting
from aiidalab_qe_vibroscopy.dielectric.workchain import workchain_and_builder
#from aiidalab_qe_eos.dielectric.result import Result
from aiidalab_qe.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "High-frequency dielectric tensor"
    #description = "High-frequency dielectric tensor using finite electric fields"

property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
#"result": Result,
}