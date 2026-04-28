import re
s = input()
print("Yes" if re.search("cat|dog", s) else "No")