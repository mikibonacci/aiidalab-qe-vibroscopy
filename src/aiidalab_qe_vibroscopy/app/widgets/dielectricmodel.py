from aiidalab_qe.common.mvc import Model
from aiida.common.extendeddicts import AttributeDict
import traitlets as tl


class DielectricModel(Model):
    vibro = tl.Instance(AttributeDict, allow_none=True)

    dielectric_data = {}
