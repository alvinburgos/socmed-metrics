import json
import csv
with open('toquery_updated.json') as f:
    data = json.load(f)
start_idx = 18

def parse_num(s):
    return int("".join(s.split(",")))

with open('additional_toquery.csv') as f:
    for row in csv.reader(f):
        new = {
            "name": row[0],
            "baseline": parse_num(row[1]),
            "category": row[2],
            "url": row[3],
            "id": start_idx
        }
        data.append(new)    
        start_idx += 1

with open('toquery_updated_v2.json', 'w') as f:
    json.dump(data, f, indent=2)
