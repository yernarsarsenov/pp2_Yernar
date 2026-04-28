import re

s = input()
cnt = len(re.findall("[A-Z]", s))
print(cnt)