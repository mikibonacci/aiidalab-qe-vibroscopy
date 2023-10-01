from aiida.orm import load_code, Dict
from aiida.plugins import WorkflowFactory
from aiida_quantumespresso.common.types import ElectronicType, SpinType

from aiida_vibroscopy.common.properties import PhononProperty

HarmonicWorkChain = WorkflowFactory("vibroscopy.phonons.harmonic")

def get_builder(codes, structure, parameters):
    protocol = parameters["workchain"].pop("protocol", "fast")
    pw_code = load_code(codes.get("pw"))
    phonopy_code = load_code(codes.get("phonopy"))
    phonon_property = PhononProperty[parameters["phonons"].pop("phonon_property","NONE")]
    dielectric_property = parameters["dielectric"].pop("dielectric_property", "dielectric")

    overrides = {
        "phonon":{
            "scf": parameters["advanced"],
        },
        "dielectric":{
            "scf": parameters["advanced"],
            "property":dielectric_property,
        },
    }
    
    builder = HarmonicWorkChain.get_builder_from_protocol(
        pw_code=pw_code,
        phonopy_code=phonopy_code,
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        phonon_property=phonon_property,
        electronic_type=ElectronicType(parameters["workchain"]["electronic_type"]),
        spin_type=SpinType(parameters["workchain"]["spin_type"]),
        initial_magnetic_moments=parameters["advanced"]["initial_magnetic_moments"],    )
    
    # MB supposes phonopy will always run serially, otherwise choose phono3py 
    # also this is needed to be set here.
    builder.phonopy.metadata.options.resources = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }

    builder.phonon.phonopy.metadata.options.resources = builder.phonopy.metadata.options.resources

    #should be automatic inside HarmonicWorkchain.
    builder.phonon.phonopy.parameters = Dict(dict={})
    builder.phonopy.parameters = builder.phonon.phonopy.parameters
    builder.phonon.phonopy.code = builder.phonopy.code

    return builder

workchain_and_builder = {
    "workchain": HarmonicWorkChain,
    "exclude": ("clean_workdir",),
    "get_builder": get_builder,
}