n = int(input())
d = dict()

for i in range(n):
    name, num = map(str, input().split())
    if name in d:
        d[name] += int(num)
    else:
        d[name] = int(num)

sorted_d = sorted(d.items())
for i, j in sorted_d:
    print(i, j)