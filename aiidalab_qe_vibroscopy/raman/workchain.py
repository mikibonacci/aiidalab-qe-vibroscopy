from aiida.orm import load_code, Dict
from aiida.plugins import WorkflowFactory

from aiida_vibroscopy.common.properties import PhononProperty

IRamanSpectraWorkChain = WorkflowFactory("vibroscopy.spectra.iraman")

def get_builder(codes, structure, parameters):
    protocol = parameters["basic"].pop("protocol", "fast")
    pw_code = load_code(codes.get("pw_code"))
    phonopy_code = load_code(codes.get("phonopy_code"))
    #phonon_property = PhononProperty[parameters.pop("phonon_property","NONE")]
    dielectric_property = parameters["iraman"]["spectrum"]
    res = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }

    overrides = {
        "phonon":{
            "scf": parameters["advance"],
            },
        "dielectric":{
            "scf": parameters["advance"],
            "property":dielectric_property,
        },
    }
    
    
    parameters = parameters["basic"]
    builder = IRamanSpectraWorkChain.get_builder_from_protocol(
        code=pw_code,
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        **parameters,
    )

    builder.phonon.phonopy.code = phonopy_code
    builder.phonon.phonopy.metadata.options.resources = res
    builder.phonon.phonopy.parameters = Dict({})

    return builder

workchain_and_builder = [IRamanSpectraWorkChain, get_builder]