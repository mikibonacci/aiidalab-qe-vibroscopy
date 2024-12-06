from __future__ import annotations
from aiidalab_qe.common.mvc import Model
import traitlets as tl
from aiida.common.extendeddicts import AttributeDict


class PowderFullModel(Model):
    vibro = tl.Instance(AttributeDict, allow_none=True)
