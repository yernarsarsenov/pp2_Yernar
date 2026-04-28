#query engine
import json, re
from functools import reduce

def get(data, path):
    try:
        tokens = re.findall(r'[a-zA-Z]+|\d+', path)
        def navigate(curr, t):
            if isinstance(curr, list):
                return curr[int(t)]
            return curr[t]
        res = reduce(navigate, tokens, data)
        if isinstance(res, str):
            return json.dumps(res)
        elif isinstance(res, (dict, list)):
            return json.dumps(res, separators=(',',':'), sort_keys=True)
        else:
            return json.dumps(res)
    except (KeyError, IndexError, TypeError):
        return "NOT_FOUND"

db = json.loads(input())
for _ in range(int(input())):
    print(get(db, input()))