import re
s = input()
pat = re.compile(r'^\d+$')
print("Match" if pat.search(s) else "No match")