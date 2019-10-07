from .base_steps import UnimplementedStep

class Recrystallize(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

class Sonicate(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

class Distill(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

    @property
    def requirements(self):
        return {
            'distillation': True,
        }

class Sublimate(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

    @property
    def requirements(self):
        return {
            'sublimation': True,
        }

class Hydrogenate(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

    @property
    def requirements(self):
        return {
            'hydrogenation': True,
        }

class Irradiate(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

    @property
    def requirements(self):
        return {
            'photochemistry': True,
        }

class Microwave(UnimplementedStep):

    def __init__(self, **kwargs):
        super().__init__(locals())

    @property
    def requirements(self):
        return {
            'microwave': True,
        }
