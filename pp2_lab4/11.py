#json patch update
import json

def patch(source, p):
    for key, val in p.items():
        if val is None:
            source.pop(key, None)
        elif isinstance(val, dict) and isinstance(source.get(key), dict):
            patch(source[key], val)
        else:
            source[key] = val
    return source

source = json.loads(input())
p = json.loads(input())
print(json.dumps(patch(source, p), sort_keys=True, separators=(',', ':')))