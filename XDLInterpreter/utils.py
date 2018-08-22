float_regex = r'([0-9]+([.][0-9]+)?)'

class XDLElement(object):

    def __init__(self):
        self.properties = {}

    def load_properties(self, properties):
        for prop in self.properties:
            if prop in properties:
                self.properties[prop] = properties[prop]