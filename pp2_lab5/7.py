import re
s = input()
p = input()
r = input()
res = re.sub(p, r, s)
print(res)