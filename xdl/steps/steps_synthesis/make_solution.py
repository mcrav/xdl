from typing import Optional, Union, List
from .add import Add
from ..base_step import Step

class MakeSolution(Step):
    """Make solution in given vessel of given solutes in given solvent.

    Args:
        solutes (str or list): Solute(s).
        solvent (str): Solvent.
        solute_masses (str or list): Mass(es) corresponding to solute(s)
        vessel (str): Vessel name to make solution in.
        solvent_volume (float): Volume of solvent to use in mL.
    """
    def __init__(
        self,
        solutes: Union[str, List[str]],
        solute_masses: Union[str, List[str]],
        solvent: str,
        vessel: str,
        solvent_volume: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = []
        self.steps.append(
            Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

        self.human_readable = f'Make solution of '
        for s, m in zip(solutes, solute_masses):
            self.human_readable += '{0} ({1} g), '.format(s, m)
        self.human_readable = self.human_readable[:-2] + ' in {solvent} ({solvent_volume} mL) in {vessel}.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }