#!/usr/bin/python

import sys
import os
import fnmatch
import yaml

yaml_files = []
for root, dirnames, filenames in os.walk('notes'):
    for filename in fnmatch.filter(filenames, '*.yaml'):
        yaml_files.append(os.path.join(root, filename))

uuids = set()
for path in yaml_files:
    # print(path)
    with open(path) as yf:
        try:
            data = yaml.load(yf)
        except:
            print('Invalid YAML file:', path)
            raise

        for note in data['notes']:
            if 'uuid' not in note:
                print(note)
                print('No UUID')
                sys.exit(1)
            uuid = note['uuid']
            if uuid in uuids:
                print('Duplicated UUID:', uuid)
                sys.exit(1)
            else:
                uuids.add(uuid)
