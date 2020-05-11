from ..errors import XDLError

class XDLReadError(XDLError):
    pass

class XDLInvalidJSONError(XDLReadError):
    pass

class XDLJSONMissingHardwareError(XDLInvalidJSONError):
    def __str__(self):
        return f'XDL JSON is missing "hardware" section.'

class XDLJSONMissingReagentsError(XDLInvalidJSONError):
    def __str__(self):
        return f'XDL JSON is missing "reagents" section.'

class XDLJSONMissingStepsError(XDLInvalidJSONError):
    def __str__(self):
        return f'XDL JSON is missing "steps" section.'

class XDLJSONHardwareNotArrayError(XDLInvalidJSONError):
    def __str__(self):
        return f'Hardware section should be an array.'

class XDLJSONReagentsNotArrayError(XDLInvalidJSONError):
    def __str__(self):
        return f'Reagents section should be an array.'

class XDLJSONStepsNotArrayError(XDLInvalidJSONError):
    def __str__(self):
        return f'Steps section should be an array.'

class XDLJSONInvalidSectionError(XDLInvalidJSONError):
    def __init__(self, section_name):
        self.section_name = section_name

    def __str__(self):
        return f'{self.section_name} is an invalid section for XDL JSON.\
 Valid section keys: "steps", "reagents", "hardware".'

class XDLInvalidStepTypeError(XDLReadError):
    def __init__(self, step_name):
        self.step_name = step_name

    def __str__(self):
        return f'"{self.step_name}" is not a valid step type.'

class XDLJSONMissingStepNameError(XDLInvalidJSONError):
    def __str__(self):
        return f'Step missing "name" parameter in XDL JSON.'

class XDLJSONMissingPropertiesError(XDLInvalidJSONError):
    def __str__(self):
        return f'XDL element must have "properties" object in XDL JSON.'
