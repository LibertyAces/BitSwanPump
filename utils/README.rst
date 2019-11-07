BSPump-utils: BSPump utils for ElasticSearch and Kibana
=======================================================

Tiny subset of BSPump

Installation
------------

``pip install bspump-utils``

Usage
-----

bselastic
^^^^^^^^^

::

  bselastic [-h] {load_index_template,cleanup,reopen,close,delete} ...

  Manage ElasticSearch.

  positional arguments:
    {load_index_template,cleanup,reopen,close,delete}
                          commands
      load_index_template
                          loads index templates into ElasticSearch
      cleanup             Closes old and deletes empty indexes
      reopen              reopen closed indexes in time range
      close               close open indexes in time range
      delete              delete indexes in time range

  optional arguments:
    -h, --help            show this help message and exit


bskibana
^^^^^^^^

::

  bskibana [-h] [--verbose] [--silent]
                {export,import,decompile,compile,rename,document} ...

  Manage Kibana object library and Kibana index in ElasticSearch.

    Example of use:

    bskibana.py export http://localhost:9200/ /tmp/kibana-index-exported.json
    bskibana.py decompile /tmp/kibana-index-exported.json /tmp/kibana-index-decompiled/ ./kibana/library/objects/
    bskibana.py compile /tmp/kibana-index-decompiled/ ./kibana/library/objects/ -o /tmp/kibana-index-exported.json
    bskibana.py import /tmp/kibana-index-exported.json http://localhost:9200/

    bskibana.py document -t ./kibana/library/templates/ ./kibana/library/objects/ -o /tmp/doc

  positional arguments:
    {export,import,decompile,compile,rename,document}
                          commands
      export              exports a Kibana index to a file
      import              Imports a Kibana index from a file
      decompile           Decompile a Kibana index file into a library
      compile             Compile a Kibana index file
      rename              Change ids of Kibana index-pattern objects and fix
                          references.
      document            Generate a documentation

  optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         Be verbose in the output
    --silent, -s          Don't print anything


Licence
-------

BSPump-utils is an open-source software, available under BSD 3-Clause License.
