import re
s = input()
print(len(re.findall(r'\b\w{3}\b', s)))