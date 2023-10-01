from aiidalab_qe_vibroscopy.phonons.settings import Setting
from aiidalab_qe_vibroscopy.phonons.workchain import workchain_and_builder
from aiidalab_qe_vibroscopy.phonons.result import Result
from aiidalab_qe.common.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "Phonon band structure"
    help = "Harmonic approximation"

property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
"result": Result,
}