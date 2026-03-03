import re
s = input()
lit = "Hello"
print("Yes" if re.match(lit, s) else "No")