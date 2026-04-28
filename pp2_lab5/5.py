#s = let, e = dig
import re
s = input()
print("Yes" if re.findall(r"^\D", s) and re.findall(r"\d$", s) else "No")