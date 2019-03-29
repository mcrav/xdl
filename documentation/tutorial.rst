========
Tutorial
========

A XDL file is an XML file consisting of three section: Hardware, Reagents and Procedure; all wrapped in an enclosing Synthesis element.

A XDL stub looks like this:

<Synthesis>
  <Hardware>
  </Hardware>

  <Reagents>
  </Reagents>

  <Procedure>
  </Procedure>
</Synthesis>

Synthesis
#########

The entire file must be wrapped in the <Synthesis> element, and the tag can also be used for specifiying global attributes.
Synthesis attributes:
* auto_clean: If True, CleanBackbone steps are added automatically between relevant steps to ensure backbone is always clean.
* organic_cleaning_reagent: Reagent to use when cleaning after steps involving organic reagents. Only relevant if auto_clean="true". Defaults to 'ether'.
* aqueous_cleaning_reagent: Reagent to use when cleaning after steps involving aqueous reagents. Only relevant if auto_clean="true". Defaults to 'water'.

