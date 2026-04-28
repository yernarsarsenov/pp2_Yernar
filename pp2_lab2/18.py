n = int(input())
a = {}

for i in range(n):
    s = input()
    if s not in a:
        a[s] = i + 1

for s in sorted(a):
    print(s, a[s])