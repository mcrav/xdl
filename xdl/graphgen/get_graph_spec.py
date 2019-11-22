from ..steps.chemputer import FilterThrough, Separate, Add

def get_graph_spec(xdl_obj):
    graph_spec = {
        'reagents': get_flask_reagents(xdl_obj),
        'buffer_flasks': get_buffer_flasks(xdl_obj),
        'cartridges': get_cartridges(xdl_obj),
        'vessels': get_vessel_spec(xdl_obj),
    }
    return graph_spec

def get_flask_reagents(xdl_obj):
    reagents = []
    for step in xdl_obj.steps:
        if type(step) == Add and step.volume != None:
            reagents.append(step.reagent)

        elif 'solvent' in step.properties and step.solvent:
            reagents.append(step.solvent)

        elif 'eluting_solvent' in step.properties and step.eluting_solvent:
            reagents.append(step.eluting_solvent)

    return sorted(list(set(reagents)))

def get_buffer_flasks(xdl_obj):
    buffer_flasks = []
    for step in xdl_obj.steps:
        if type(step) == FilterThrough and step.from_vessel == step.to_vessel:
            buffer_flasks.append({'n_required': 1, 'connected_node': step.from_vessel})

        elif type(step) == Separate:
            n_required = step.buffer_flasks_required
            if n_required:
                buffer_flasks.append({
                    'n_required': n_required,
                    'connected_node': step.separation_vessel
                })

    return buffer_flasks

def get_cartridges(xdl_obj):
    cartridges = []
    for step in xdl_obj.steps:
        if type(step) == FilterThrough:
            cartridges.append({
                'from': step.from_vessel,
                'from_type': xdl_obj.hardware[step.from_vessel].component_type,
                'to': step.to_vessel,
                'to_type': xdl_obj.hardware[step.to_vessel].component_type,
                'chemical': step.through
            })

        elif type(step) == Separate and step.through:
            cartridges.append({
                'from': step.separation_vessel,
                'from_type': 'separator',
                'to': step.to_vessel,
                'to_type': xdl_obj.hardware[step.to_vessel].component_type,
                'chemical': step.through,
            })
    return cartridges

def get_vessel_spec(xdl_obj):
    vessel_spec = {}
    component_types = []
    for component in xdl_obj.hardware:
        if not component.component_type == 'cartridge':
            component_types.append((component.id, component.component_type))
    vessel_spec['types'] = component_types
    vessel_spec['temps'] = {}
    for step in xdl_obj.steps:
        for vessel, reqs in step.requirements.items():
            actual_vessel = step.properties[vessel]
            for prop, val in reqs.items():
                if prop == 'temp':
                    if not actual_vessel in vessel_spec['temps']:
                        vessel_spec['temps'][actual_vessel] = {}
                    if not prop in vessel_spec['temps'][actual_vessel]:
                        vessel_spec['temps'][actual_vessel] = []
                    vessel_spec['temps'][actual_vessel].extend(val)
    return vessel_spec
