import re
s = input()
print(*re.findall(r'\d{2,}', s))