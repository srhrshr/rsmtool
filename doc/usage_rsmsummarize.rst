.. _usage_rsmsummarize:

``rsmsummarize`` - Compare multiple scoring models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

RSMTool provides the ``rsmsummarize`` command-line utility to compare multiple models and to generate a comparison report. Unlike ``rsmcompare`` which creates a detailed comparison report between the two models, ``rsmsummarize`` can be used to create a more general overview of multiple models. 

``rsmsummarize`` can be used to compare:

1. Multiple ``rsmtool`` experiments, or
2. Multiple ``rsmeval`` experiments, or
3. A mix of ``rsmtool`` and ``rsmeval`` experiments (in this case, only the evaluation analyses will be compared).


.. note::

    It is strongly recommend that the original experiments as well as the summary experiment are all done using the same version of RSMTool.

.. include:: tutorial_rsmsummarize.rst

Input
"""""

``rsmsummarize`` requires a single argument to run an experiment: the path to :ref:`a configuration file <config_file_rsmsummarize>`. You can specify which models you want to compare and the name of the report by supplying the path to :ref:`a configuration file <config_file_rsmsummarize>`. It can also take an output directory as an optional second argument. If the latter is not specified, ``rsmsummarize`` will use the current directory as the output directory.

Here are all the arguments to the ``rsmsummarize`` command-line script.

.. program:: rsmsummarize

.. option:: config_file 

    The :ref:`JSON configuration file <config_file_rsmsummarize>` for this experiment.

.. option:: output_dir (optional)

    The output directory where the report files for this comparison will be stored.

.. option:: -h, --help

    Show help message and exist.

.. option:: -V, --version

    Show version number and exit.

.. include:: config_rsmsummarize.rst

Output
""""""
``rsmsummarize`` produces the comparison report in HTML format as well as in the form of a Jupyter notebook (a ``.ipynb`` file) in the output directory.
