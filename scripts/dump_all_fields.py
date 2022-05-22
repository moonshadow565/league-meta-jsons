#!/bin/env python3
import json
import os
import sys
import glob

def fnv1a(s):
    h = 0x811c9dc5
    for b in s.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h

results = set()
for filename in glob.iglob(f"{sys.argv[1]}/**/*.json", recursive=True):
    with open(filename) as infile:
        for klass in json.load(infile)["classes"]:
            for prop in klass["properties"]:
                h = prop["hash"]
                if h:
                    results.add(h)
results = sorted([ f"{x:08x}" for x in results ])
print('\n'.join(results))