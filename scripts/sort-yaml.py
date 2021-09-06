#!/usr/bin/env python3

import sys

import yaml

from pyuca import Collator
c = Collator()

FILENAME = sys.argv[1]

with open(FILENAME) as f:
    # load yaml as dictionary items
    data = yaml.safe_load(f).items()

    # sort based on the keys using pyuca
    data = sorted(data, key=lambda x: c.sort_key(x[0]))

    # convert back to a dictionary
    data = dict(data)


with open(FILENAME, "w") as g:
    yaml.dump(data, g, sort_keys=False, allow_unicode=True)
