import re
line = input()
m = re.search(r'Name: (.+), Age: (.+)', line)
print(m.group(1), m.group(2))