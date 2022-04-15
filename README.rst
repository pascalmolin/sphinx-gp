Sphinx-gp
======================================================================

Add gp session in sphinx documents.

Usage
----------------------------------------------------------------------

Add and configure in ``conf.py``::

  extensions += ['sphinxcontrib.gp']

  app.add_config_value('gp_version', '2.12', False)
  # if set, do not load the local gp files provided here
  app.add_config_value('gp_js_path',
	    'https://webusers.imj-prg.fr/~pascal.molin/static/gp.2.14',
	    False)
	
  rstprog = [
    # ( extension, begin rstcomment, end rstcomment ),
    ('.gp', '/**', '**/' ),
    ('.c', '/**', '**/' ),
    ]

Installation
----------------------------------------------------------------------

In this repository

::
  
  pip install .


