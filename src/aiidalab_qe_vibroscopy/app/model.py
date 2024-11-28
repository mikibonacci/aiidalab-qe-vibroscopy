import traitlets as tl


from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel


class VibroConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    dependencies = [
        "input_structure",
    ]

    simulation_type_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])),
        default_value=[
            ("IR/Raman, Phonon, Dielectric, INS properties", 1),
            ("IR/Raman and Dielectric in Primitive Cell Approach", 2),
            ("Phonons for non-polar materials and INS", 3),
            ("Dielectric properties", 4),
        ],
    )
    simulation_type = tl.Int(1)

    symmetry_symprec = tl.Float(1e-5)
    supercell_x = tl.Int(2)
    supercell_y = tl.Int(2)
    supercell_z = tl.Int(2)

    supercell = tl.List(
        trait=tl.Int(),
        default_value=[2, 2, 2],
    )

    def _get_default(self, trait):
        return self._defaults.get(trait, self.traits()[trait].default_value)
