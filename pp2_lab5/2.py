import re
s = input()
p = input()
print("Yes" if re.search(p, s) else "No")