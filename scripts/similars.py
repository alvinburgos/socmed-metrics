from glob import glob
from difflib import get_close_matches
import json
import csv

names = set()
for path in glob('data/*.json'):
    with open(path) as f:
        for line in f:
            name = json.loads(line)["name"]
            names.add(name)
print(names)

with open('Oct2024.csv') as f:
    for seq, row in enumerate(csv.reader(f)):
        if seq == 0:
            continue
        if row[0] == '':
            continue
        name = row[0]
        matches = get_close_matches(name, names, n=3, cutoff=0.4)
        print(f"for name {name}, matches = {matches}")
