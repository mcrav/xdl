def get_xdl_string(xdltree):
    """Convert XDL etree to pretty XML string.
    
    Arguments:
        xdltree {lxml.etree.ElementTree} -- etree of XDL

    Returns:
        str -- XML string
    """
    indent = '  '
    # Synthesis tag
    s = '<Synthesis>\n'
    indent_level = 1
    # Hardware, Reagents and Procedure tags
    for element in xdltree.findall('*'):
        s += f'{indent * indent_level}<{element.tag}>\n'
        indent_level += 1
        # Component, Reagent and Step tags
        for element2 in element.findall('*'):
            s += f'{indent * indent_level}<{element2.tag}\n'
            indent_level += 1
            # Element Properties
            for attr, val in element2.attrib.items():
                if val:
                    s += f'{indent * indent_level}{attr}="{val}"\n'
            s = s[:-1] + ' />\n'
            indent_level -= 1
        indent_level -= 1
        s += f'{indent * indent_level}</{element.tag}>\n\n'
    s += '</Synthesis>\n'
    return s
