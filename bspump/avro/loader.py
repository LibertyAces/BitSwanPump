#!/usr/bin/env python3
import json
import fastavro
import logging



###

L = logging.getLogger(__name__)

###


def load_avro_schema(config):
    schema = config.get('schema')
    if schema == '':
        schema_file = config.get('schema_file')
        if schema_file != '':
            with open(schema_file, 'r') as fi:
                schema = json.load(fi)

    if schema == '':
        raise RuntimeError("AVRO schema is not configured.")

    return fastavro.parse_schema(schema)
