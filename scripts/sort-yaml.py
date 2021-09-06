#!/usr/bin/env python3

import sys

import yaml

from pyuca import Collator
c = Collator()

FILENAME = sys.argv[1]

with open(FILENAME) as f:
    # load yaml
    data = yaml.safe_load(f)

    # sort based on the keys using pyuca
    data = dict(sorted(data.items(), key=lambda x: c.sort_key(x[0])))


with open(FILENAME, "w") as g:
    yaml.dump(data, g, sort_keys=False, allow_unicode=True)
