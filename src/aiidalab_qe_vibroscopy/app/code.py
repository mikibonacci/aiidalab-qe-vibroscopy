from aiidalab_qe.common.code.model import CodeModel, PwCodeModel
from aiidalab_qe.common.panel import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


class VibroResourceSettingsModel(PluginResourceSettingsModel):
    """Resource settings for the vibroscopy calculations."""

    title = "Vibronic resources"
    identifier = "vibronic"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        code_models = {
            "phonon": PwCodeModel(
                name="phonon",
                description="pw.x for phonons",
                default_calc_job_plugin="quantumespresso.pw",
            ),
            "dielectric": PwCodeModel(
                name="dielectric",
                description="pw.x for dielectric",
                default_calc_job_plugin="quantumespresso.pw",
            ),
            "phonopy": CodeModel(
                name="phonopy",
                description="phonopy",
                default_calc_job_plugin="phonopy.phonopy",
            ),
            "pythonjob": CodeModel(
                name="pythonjob",
                description="Python job for MACE",
                default_calc_job_plugin="pythonjob.pythonjob",
            ),
        }

        # if has_mace:
        #     code_models.update(
        #         {
        #                 "pythonjob": CodeModel(
        #                 name="pythonjob",
        #                 description="Python job for MACE",
        #                 default_calc_job_plugin="pythonjob.pythonjob",
        #             ),
        #         }
        #     )

        self.add_models(code_models)


class VibroResourcesSettingsPanel(
    PluginResourceSettingsPanel[VibroResourceSettingsModel]
):
    """Panel for the resource settings for the vibroscopy calculations."""

    title = "Vibronic"
