from .base_step import Step

class Recrystallization(Step):

    def __init__(self):
        super().__init__(locals())

        self.steps = [

        ]

        self.human_readable = 'Do recrystallisation.'

class VacuumDistillation(Step):

    def __init__(self):
        super().__init__(locals())

        self.steps = [

        ]

        self.human_readable = 'Do vacuum distillation.'
