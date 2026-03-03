import re
s = input()
print(len(re.findall(r'\d{2}/\d{2}/\d{4}', s)))