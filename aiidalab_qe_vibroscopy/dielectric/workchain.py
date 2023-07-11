from aiida.orm import load_code, Str
from aiida.plugins import WorkflowFactory

from aiida_vibroscopy.common.properties import PhononProperty

DielectricWorkChain = WorkflowFactory("vibroscopy.dielectric")


'''
The logic is that HarmonicWorkchain can run PhononWorkchain and DielectricWorkchain, skipping the second
but not the first: so we add also the possibility to run only DielectricWorkchain.
'''

def get_builder(codes, structure, parameters):
    protocol = parameters["basic"].pop("protocol", "fast")
    pw_code = load_code(codes.get("pw_code"))
    dielectric_property = parameters["dielectric"].pop("dielectric_property", "none")

    '''
    here we set a readable input anyway, even if we do not run this workflow 
    but only the HarmonicWorkchain for phonons-only calculations.
    The problem is that if we select both Dielectric and Phonons calculations,
    this protocol is called, even if never used. 
    '''
    if dielectric_property == "none": dielectric_property = "dielectric"

    overrides = {
        "scf": parameters["advance"],
        "property":dielectric_property,
    }
    
    parameters = parameters["basic"]
    

    builder = DielectricWorkChain.get_builder_from_protocol(
        code=pw_code,
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        **parameters,
    )

    builder.pop("clean_workdir", None)

    
    return builder

workchain_and_builder = [DielectricWorkChain, get_builder]