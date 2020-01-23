==============
Usage Tutorial
==============

Generating XDL file
*******************
XDL files can be written manually, but the easiest way to produce them is from
written procedures using `SynthReader <http://chemify.us-east-2.elasticbeanstalk.com/synthreader>`_.

If the XDL produced by `SynthReader <http://chemify.us-east-2.elasticbeanstalk.com/synthreader>`_
is not correct, the written procedure can be altered to aid translation, for example,
by converting present tense to past tense, and removing unnecessary detail.

Load XDL Object
***************
::

    from xdl import XDL

    xdl_obj = XDL('procedure.xdl')

Generate Experiment Graph
*************************

Template graphs can be created here and should detail your entire setup, without
reagent flasks or cartridges. Basically, the template should be the same between
different syntheses, whereas the experiment graph is specific to one synthesis.
Graphs can be edited `here <http://chemify.us-east-2.elasticbeanstalk.com/graph>`_.

::

    # Produces graph file named 'procedure_graph.json'.
    xdl_obj.graph('template.json')

Compile XDL and Graph
*********************

Once you are happy with both the graph and the XDL, they can be compiled into
a .xdlexe file.

::

    # Produces executable file named 'procedure.xdlexe'.
    xdl_obj.prepare_for_execution('procedure_graph.json')

Load and Run XDL Executable
***************************

The executable can be inspected to see a full breakdown of what actions will be
taken upon execution. Once you are ready to run the xdlexe, it is just a matter of
instantiating the platform controller, and passing it to the xdlexe execute method.
It is advisable to first execute in simulation mode, before running on a physical
platform. Simulation is toggled within the platform controller.

::

    xdlexe = XDL('procedure.xdlexe')

    xdlexe.execute(platform_controller)

Instantiating the Platform Controller
*************************************

This depends on the platform being used, but as an example, the Chemputer
platform controller instantiation is shown here.

::

    from chempiler import Chempiler
    import ChemputerAPI

    platform_controller = Chempiler(
        experiment_code="procedure",
        output_dir="/path/to/experiment_folder",
        graph_file="procedure_graph.json",
        device_modules=[ChemputerAPI],
        simulation=True,
    )
