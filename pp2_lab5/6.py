#email
import re
s = input()
sub = re.search(r"\S+@\S+\.\S+", s)
print(sub.group() if sub else "No email")