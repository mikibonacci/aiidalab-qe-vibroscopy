from aiida.orm import load_code
from aiida.plugins import WorkflowFactory

from aiida_vibroscopy.common.properties import PhononProperty

PhononWorkChain = WorkflowFactory("vibroscopy.phonons.phonon")


def get_builder(codes, structure, parameters):
    protocol = parameters["basic"].pop("protocol", "fast")
    pw_code = load_code(codes.get("pw_code"))
    phonopy_code = load_code(codes.get("phonopy_code"))
    phonon_property = PhononProperty[parameters["phonons"]["phonon_property"]]

    overrides = {
        "phonon":{
            "scf": parameters["advance"],
        },
    }
    
    parameters = parameters["basic"]
    builder = PhononWorkChain.get_builder_from_protocol(
        pw_code=pw_code,
        phonopy_code=phonopy_code,
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        phonon_property=phonon_property,
        **parameters,
    )
    
    # MB supposes phonopy will always run serially, otherwise choose phono3py 
    # also this is needed to be set here.
    builder.phonopy.metadata.options.resources = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }
    
    return builder

workchain_and_builder = [PhononWorkChain, get_builder]