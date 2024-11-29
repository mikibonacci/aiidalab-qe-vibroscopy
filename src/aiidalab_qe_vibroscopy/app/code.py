from aiidalab_qe.common.code.model import CodeModel, PwCodeModel
from aiidalab_qe.common.panel import ResourceSettingsModel, ResourceSettingsPanel


class VibroResourceSettingsModel(ResourceSettingsModel):
    """Resource settings for the vibroscopy calculations."""

    codes = {
        "phonon": PwCodeModel(
            description="pw.x for phonons",
            default_calc_job_plugin="quantumespresso.pw",
        ),
        "dielectric": PwCodeModel(
            description="pw.x for dielectric",
            default_calc_job_plugin="quantumespresso.pw",
        ),
        "phonopy": CodeModel(
            name="phonopy",
            description="phonopy",
            default_calc_job_plugin="phonopy.phonopy",
        ),
    }


class VibroResourcesSettingsPanel(ResourceSettingsPanel[VibroResourceSettingsModel]):
    """Panel for the resource settings for the vibroscopy calculations."""

    title = "Vibronic"
    identifier = identifier = "vibronic"
