.. _config_file_rsmsummarize:

Experiment configuration file
"""""""""""""""""""""""""""""

This is a file in ``.json`` format that provides overall configuration options for an ``rsmsummarize`` experiment. Here's an example configuration file for `rsmsummarize <https://github.com/EducationalTestingService/rsmtool/blob/master/examples/rsmsummarize/config_rsmsummarize.json>`_.

There are two required fields and the rest are all optional.

summary_id
~~~~~~~~~~~~~~~~~~~~~~~
An identifier for the ``rsmsummarize`` experiment. This will be used to name the report. It can be any combination of alphanumeric values, must *not* contain spaces, and must *not* be any longer than 200 characters.


experiment_dirs
~~~~~~~~~~~~~~~
The list of the directories with the results of the experiment. These directories should be the output directories used for each experiment and should contain subdirectories ``output`` and ``figure`` generated by ``rsmtool`` or ``rsmeval``.


description *(Optional)*
~~~~~~~~~~~~~~~~~~~~~~~~
A brief description of the summary. The description can contain spaces and punctuation.

.. _general_sections_rsmsummarize:

general_sections *(Optional)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RSMTool provides pre-defined sections for ``rsmsummarize`` (listed below) and, by default, all of them are included in the report. However, you can choose a subset of these pre-defined sections by specifying a list as the value for this field.

    - ``preprocessed_features`` : compares marginal and partial correlations between all features and the human score, and optionally response length if this was computed for any of the models.

    - ``model``: Compares the parameters of the two regression models. For linear models, it also includes the standardized and relative coefficients.

    - ``evaluation``: Compares the standard set of evaluations recommended for scoring models on the evaluation data.

    - ``sysinfo``: Shows all Python packages along with versions installed in the current environment while generating the report.



.. _custom_sections_rsmsummarize:

custom_sections *(Optional)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A list of custom, user-defined sections to be included into the final report. These are IPython notebooks (``.ipynb`` files) created by the user.  The list must contains paths to the notebook files, either absolute or relative to the configuration file. All custom notebooks have access to some :ref:`pre-defined variables <custom_notebooks>`.

.. _special_sections_rsmsummarize:

special_sections *(Optional)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A list specifying special ETS-only comparison sections to be included into the final report. These sections are available *only* to ETS employees via the `rsmextra` package.

section_order *(Optional)*
~~~~~~~~~~~~~~~~~~~~~~~~~~
A list containing the order in which the sections in the report should be generated. Any specified order must explicitly list:

    1. Either *all* pre-defined sections if a value for the :ref:`general_sections <general_sections_rsmsummarize>` field is not specified OR the sections specified using :ref:`general_sections <general_sections_rsmsummarize>`, and

    2. *All* custom section names specified using :ref:`custom_ sections <custom_sections_rsmsummarize>`, i.e., file prefixes only, without the path and without the `.ipynb` extension, and

    3. *All* special sections specified using :ref:`special_sections <special_sections_rsmsummarize>`.
