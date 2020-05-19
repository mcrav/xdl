import os
import re

template = '''
<html>
  <head>
  <link
    rel="stylesheet"
    href=
"https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh"
    crossorigin="anonymous">
  </head>
  <body class="p-4">
    <div class="container">
    <h2 class="mb-5">XDL Cross-Platform Standard 1.0</h2>
      <p><b>Steps overview:</b> {step_names}</p>
      {steps}
      <h3 class="mb-3 mt-5">Platform Compatibility (WIP)</h3>
      {platform_compat_table}
    </div>
  </body>
</html>
'''

step_template = '''
    <div class="row my-5">
    <div class="col">
    <h4>{name}</h4>
    <p><i>{description}</i></p>
    <table class="table tabled-bordered">
      <thead>
        <tr>
        <th>Property</td>
        <th>Type</td>
        <th>Description</td>
        </tr>
      </thead>
      <tbody>
        {property_rows}
      </tbody>
    </table>
    </div>
    </div>
    <hr/>
'''

property_row_template = '''
        <tr>
          <td><code style="color: #4e4ece">{property}</code></td>
          <td><code style="color: #0b8962;">{property_type}</code></td>
          <td>{description}</td>
        </tr>
'''

HERE = os.path.abspath(os.path.dirname(__file__))

def parse_templates():
    files = [f for f in os.listdir(HERE) if f.endswith('.py')]

    # Ignore this file  __init__ and abstract template
    files = [
        f for f in files
        if not f.startswith(('abstract', 'generate', '_'))
    ]

    steps = []

    for f in files:
        with open(os.path.join(HERE, f)) as fd:
            lines = fd.readlines()
        name = ''
        description = ''
        append_description = False
        read_props = False
        current_prop = {}
        properties = []
        read_default_props = False
        default_props = []
        for line in lines:

            # Starting new class, append and reset
            if line.startswith('class Abstract') and name:
                steps.append({
                    'name': name,
                    'description': description,
                    'properties': properties,
                })
                name = ''
                description = ''
                append_description = False
                read_props = False
                current_prop = {}
                properties = []
                default_props = []

            line = line.strip()

            # Get name
            if line.startswith('MANDATORY_NAME = '):
                name = re.search(r"MANDATORY_NAME = '([a-zA-Z]+)'", line)[1]

            # Description finished
            if line.startswith('Name: '):
                append_description = False

            # Append multiple lines to description.
            if append_description and line:
                description += ' ' + line

            # Get description
            if line.startswith('"""'):
                if not description:
                    description += line.split('"""')[1]
                    append_description = True
                elif read_props:
                    if current_prop:
                        properties.append(current_prop)
                    read_props = False

            # End of dictionary, not reading default props
            if line.startswith('}'):
                if default_props:
                    for prop in properties:
                        if prop['name'] in default_props:
                            prop['description'] =\
                                'Optional. ' + prop['description']
                    default_props = []
                read_default_props = False

            if read_default_props:
                default_props.append(re.match(r"'([a-z_]+)': ", line)[1])

            # Read properties
            if read_props:

                # Allow 'str', 'int', 'Union[List, str]' etc
                prop_type_pattern = r'[,\[\] a-zA-Z]'

                # Search for "var_name (var_type):" pattern
                new_prop = re.match(
                    r'([a-z_]+) \((' + prop_type_pattern + r'+)\):', line)
                if new_prop:
                    if current_prop:
                        properties.append(current_prop)

                    # Search for description coming after "var_name (var_type):"
                    description_pattern = r'[a-z_]+ \(' + prop_type_pattern\
                        + r'+\): (.*)$'
                    current_prop = {
                        'name': new_prop[1],
                        'type': new_prop[2],
                        'description': re.match(description_pattern, line)[1]
                    }

                # Append multiline description
                elif current_prop:
                    current_prop['description'] += ' ' + line

            if line.startswith('Mandatory props:'):
                read_props = True

            if line.startswith('MANDATORY_DEFAULT_PROPS ='):
                read_default_props = True

        steps.append({
            'name': name,
            'description': description,
            'properties': properties,
        })

    return sorted(steps, key=lambda step: step['name'])

def platform_compat_table():
    compat_matrix = [
        ['Add', True, True, True, False],
        ['Transfer', True, True, True, False],
        ['Stir', True, True, False, False],
        ['StartStir', True, True, False, False],
        ['StopStir', True, True, False, False],
        ['HeatChill', True, True, False, False],
        ['HeatChillToTemp', True, True, False, False],
        ['StartHeatChill', True, True, False, False],
        ['StopHeatChill', True, True, False, False],
        ['Purge', True, False, False, False],
        ['StartPurge', True, False, False, False],
        ['StopPurge', True, False, False, False],
        ['CleanVessel', True, False, False, False],
        ['Evaporate', True, False, False, False],
        ['Filter', True, False, False, False],
        ['WashSolid', True, False, False, False],
        ['Dry', True, False, False, False],
        ['Separate', True, False, False, False],
        ['Dissolve', True, False, False, False],
        ['EvacuateAndRefill', True, False, False, False],
        ['FilterThrough', True, False, False, False],
        ['Precipitate', True, False, False, False],
        ['Recrystallize', True, False, False, False],
        ['RunColumn', True, False, False, False],
        ['Separate', True, False, False, False]
    ]
    table = '''
<table class="table table-bordered">
  <thead>
    <tr>
      <th>Step</th>
      <th>Chemputer</th>
      <th>SMS</th>
      <th>N9</th>
      <th>ChemSpeed</th>
    </tr>
  </thead>
  <tbody>
    '''
    green = '#ccffcc'
    red = '#ffcccc'
    for row in compat_matrix:
        colors = []
        for flag in row[1:]:
            if flag:
                colors.append(green)
            else:
                colors.append(red)
        table += f'''
<tr>
  <td>{row[0]}</td>
  <td style="background-color: {colors[0]}"></td>
  <td style="background-color: {colors[1]}"></td>
  <td style="background-color: {colors[2]}"></td>
  <td style="background-color: {colors[3]}"></td>
</tr>
'''
    table += '</tbody></table>'
    return table

def generate_doc(save=None):
    steps = parse_templates()
    steps_html = ''
    for step in steps:
        props_html = ''
        for prop in step['properties']:
            props_html += property_row_template.format(**{
                'property': prop['name'],
                'property_type': prop['type'],
                'description': prop['description']
            })
        step_html = step_template.format(**{
            'name': step['name'],
            'description': step['description'],
            'property_rows': props_html,
        })
        steps_html += step_html
    html = template.format(**{
        'steps': steps_html,
        'step_names': ', '.join([step['name'] for step in steps]),
        'platform_compat_table': platform_compat_table()
    })
    if save:
        with open(save, 'w') as fd:
            fd.write(html)
    return html
