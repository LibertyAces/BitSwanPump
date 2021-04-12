#!/usr/bin/env python3
import json
import fastavro
import logging



###

L = logging.getLogger(__name__)

###


def load_avro_schema(config):
        schema_file = config.get('schema_file')
        if schema_file != '':
            with open(schema_file, 'r') as fi:
                schema = json.load(fi)
            return fastavro.parse_schema(schema)
        return
