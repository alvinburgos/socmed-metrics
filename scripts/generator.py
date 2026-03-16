import json
import arrow
import random
from io import StringIO

r = random.SystemRandom(143)

with open('toquery_updated.json') as f:
    stuff = json.load(f)
    
def nextval(x: int) -> int:
    mul = r.uniform(1.01, 1.10)
    return int(mul * x)

data = StringIO()

for seq, o in enumerate(stuff):
    o['id'] = seq
    start = arrow.get('2025-01-01')
    end = arrow.get('2025-02-01')
    val = r.randrange(10000, 100000)
    for curr in arrow.Arrow.range('day', start, end):
        o['date'] = curr.date().isoformat()
        o['follows'] = val
        data.write(json.dumps(o))
        data.write('\n')
        val = nextval(val)

print(data.getvalue())
