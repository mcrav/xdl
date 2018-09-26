import abc
from lxml import etree
from ..constants import DEFAULT_VALS
from ..utils import XDLElement


class Step(XDLElement):

    def __init__(self):
        self.name = ''
        self.properties = {}
        self.steps = []

    def as_chasm(self):
        chasm = self.get_chasm_stub()
        for step in self.steps:
            chasm.add_step(step)
        return chasm.code

    def get_chasm_stub(self):
        chasm = Chasm()
        if self.properties['comment']:
            chasm.add_comment(self.properties['comment'])
        return chasm

    def as_xdl(self, as_str=False):
        step = etree.Element('step')
        step.set('name', self.name)
        for prop, val in self.properties.items():
            if val != '':
                element = etree.SubElement(step, 'property')
                element.set('name', prop)
                element.text = str(val)
        if as_str:
            return etree.dump(step)
        else:
            return step

    def load_properties(self, properties):
        new_properties = {}
        for prop, val in properties.items():
            if prop in self.properties:
                new_properties[prop] = val
        self.__init__(**new_properties)

    def update_steps(self):
        self.__init__(**self.properties)

    def execute(self, chempiler):
        for step in self.steps:
            step.execute(chempiler)

class Comment(Step):

    def __init__(self, comment=''):
        self.comment = comment

        self.name = 'Comment'
        self.properties = {
            'comment': self.comment,
        }

    def as_chasm(self):
        chasm = Chasm()
        chasm.add_comment(self.properties['comment'])
        return chasm.code

class Repeat(Step):
    """
    Repeat given step given number of times.
    """
    def __init__(self, repeat_n_times=1, steps=[], comment=''):
        """
        Arguments:
            repeat_n_times {int} -- Number of times to repeat given step.
            steps {List[Step]} -- List of Step objects.
        """
        if isinstance(steps, Step):
            steps = [steps]

        self.name = 'Repeat'
        self.properties = {
            'repeat_n_times': repeat_n_times,
            'steps': steps,
            'comment': comment,
        }
        self.steps = []
        for i in range(repeat_n_times):
            self.steps.extend(self.properties['steps'])

        self.human_readable = f'Do the folllowing {repeat_n_times}:\n'
        for step in steps:
            self.human_readable += step.human_readable

    def as_chasm(self):
        chasm = Chasm()
        chasm.add_for(3, self.properties['steps'])
        return chasm.code

    def as_xdl(self, as_str=False):
        root = etree.Element('step')
        root.set('name', self.name)
        for prop, val in self.properties.items():
            if val != '':
                propelement = etree.SubElement(root, 'property')
                if prop != 'steps':
                    propelement.text = str(val)
                    propelement.set('name', prop)
                else:
                    for step in self.properties['steps']:
                        propelement.append(step.as_xdl())
        if as_str:
            return etree.dump(root)
        else:
            return root

    def load_properties(self, properties):
        for prop in self.properties:
            if prop in properties:
                self.properties[prop] = properties[prop]
            
            
