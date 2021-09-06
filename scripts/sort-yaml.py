#!/usr/bin/env python3

import sys

import yaml

from pyuca import Collator
c = Collator()

FILENAME = sys.argv[1]

with open(FILENAME) as f:
    data = dict(sorted(yaml.safe_load(f).items(), key=lambda x: c.sort_key(x[0]))).items()

yaml.add_representer(type({}.items()), yaml.representer.SafeRepresenter.represent_dict)

with open(FILENAME, "w") as g:
    yaml.dump(data, g, allow_unicode=True)
