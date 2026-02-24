#deep diff
import json

def diff(a, b, path=""):
    res = []
    keys = set(a) | set(b) if isinstance(a, dict) and isinstance(b, dict) else set()

    for key in keys:
        p = f"{path}.{key}" if path else key
        v1 = a.get(key)
        v2 = b.get(key)

        if isinstance(v1, dict) and isinstance(v2, dict):
            res.extend(diff(v1, v2, p))
        elif v1 != v2:
            s1 = json.dumps(v1, separators=(',',':')) if key in a else "<missing>"
            s2 = json.dumps(v2, separators=(',',':')) if key in b else "<missing>"
            res.append(f"{p} : {s1} -> {s2}")
    return res


a = json.loads(input())
b = json.loads(input())
diffs = sorted(diff(a, b))
print('\n'.join(diffs) or "No differences")