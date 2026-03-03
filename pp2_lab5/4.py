#all nums
import re
s = input()
print(' '.join(re.findall(r'\d', s)))