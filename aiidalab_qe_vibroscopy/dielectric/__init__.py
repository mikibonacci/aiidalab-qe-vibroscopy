from aiidalab_qe_vibroscopy.dielectric.settings import Setting
from aiidalab_qe_vibroscopy.dielectric.workchain import workchain_and_builder
#from aiidalab_qe_vibroscopy.dielectric.result import Result
from aiidalab_qe.common.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "High-frequency dielectric tensor"
    help = "High-frequency dielectric tensor"
    
property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
#"result": Result,
}