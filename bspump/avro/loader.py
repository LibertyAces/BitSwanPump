#!/usr/bin/env python3
import json
import fastavro
import logging



###

L = logging.getLogger(__name__)

###

"""
This module returns a 'schema' if 'schema_file' key is passed in the configuration.

In the case schema_file is absent it returns 'None'.
"""


def load_avro_schema(config):
    schema_file = config.get('schema_file')
    if schema_file == '':
        return None
    else:
        try:
            with open(schema_file, 'r') as fi:
                schema = json.load(fi)
            return fastavro.parse_schema(schema)
        except Exception as e:
            L.error("Schema file is incorrect")



