ewoks |version|
===============

.. image:: https://img.shields.io/badge/DOI-10.1080/08940886.2024.2432305-blue
   :target: https://doi.org/10.1080/08940886.2024.2432305


**Ewoks is an ecosystem of Python packages designed to execute computational graphs**, also known as workflows.

In these workflows:

- **Nodes** represent processing steps
- **Links** represent data flowing between steps

.. image:: https://gitlab.esrf.fr/workflow/ewokstutorials/ewoksfordevs/-/raw/main/images/workflow1.excalidraw.svg?ref_type=heads

Many `workflow management systems <https://s.apache.org/existing-workflow-systems>`_ exist to
deal with data processing problems by expressing them as *workflows*.

Ewoks acts as a **bridge between workflow systems**, enabling the same workflow to be executed across different systems.
Any workflow system can be integrated into Ewoks as an `execution engine <./engines.html>`_, allowing interoperability without
changing the workflow definition or implementation.

Workflows can be defined using **JSON**, **YAML**, or created programmatically in Python following the
`Ewoks specification <https://ewokscore.readthedocs.io/en/stable/reference/specs.html>`_.

*ewoks* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_
of the `European Synchrotron <https://www.esrf.eu/>`_.

.. admonition:: Quick Start

   Install *ewoks*

   .. code-block:: bash

      pip install ewoks

   Execute the demo workflow

   .. code-block:: bash

      ewoks execute demo --test

.. toctree::
   :hidden:
    
   tutorials
   howtoguides
   explanations
   reference
