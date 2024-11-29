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

    #Control for disable the supercell widget

    disable_x = tl.Bool(False)
    disable_y = tl.Bool(False)
    disable_z = tl.Bool(False)

    supercell = tl.List(
        trait=tl.Int(),
        default_value=[2, 2, 2],
    )

    def _get_default(self, trait):
        return self._defaults.get(trait, self.traits()[trait].default_value)
    
    def on_input_structure_change(self, _=None):

        if not self.input_structure:
            self._get_default()

        else:

            self.disable_x, self.disable_y, self.disable_z = True, True, True
            pbc = self.input_structure.pbc

            if pbc == (False,False, False):
                # No periodicity; fully disable and reset supercell
                self.supercell_x = self.supercell_y = self.supercell_z = 1
            elif pbc == (True, False, False):
                self.supercell_y = self.supercell_z = 1
                self.disable_x = False
            elif pbc == (True, True, False):
                self.supercell_z = 1
                self.disable_x = self.disable_y = False
            elif pbc == (True, True, True):
                self.disable_x = self.disable_y = self.disable_z = False

        
            self.supercell = [self.supercell_x, self.supercell_y, self.supercell_z]
