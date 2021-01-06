================
Future Proposals
================

Placeholder page for proposals for future versions of the XDL standard.

Metadata section
****************

Proposed is a ``Metadata`` section containing extra information about the procedure. This would be on the same level as ``Procedure``, ``Reagents`` and ``Hardware``, and would be optional. An exact specification of the proposed metadata fields is shown below.

.. csv-table:: Metadata fields
   :header: "Field", "Type", "Description"

   "``description``", "``str``", "Optional. Brief description of the synthesis."
   "``publication``", "``str``", "Optional. Publication synthesis was taken from."
   "``smarts``", "``str``", "Optional. SMARTS string of the transformation."
   "``product``", "``str``", "Optional. Name of product.",
   "``product_inchi``", "``str``", "Optional. INCHI string of product.",
   "``product_cas``", "``int``", Optional. CAS number of product.",
   "``product_vessel``", "``str``", "Optional. XDL vessel that the product is in at the end of the procedure."
   "``reaction_class``", "``str``", "Optional. Type of reaction being carried out. At the moment, not limited to specific options, as reaction classification can be ambiguous."
   "``comment``", "``str``", "Optional. Unrestricted comment field."
