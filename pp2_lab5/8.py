import re
s = input()
d = input()
res = re.split(d, s)
print(",".join(res))