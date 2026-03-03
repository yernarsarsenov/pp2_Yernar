import re
s = input()
pat = re.compile(r'\w+')
print(len(re.findall(pat, s)))