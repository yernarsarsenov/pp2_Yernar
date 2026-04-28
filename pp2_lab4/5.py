def count(n):
    for i in range(n, -1, -1):
        yield i
n = int(input())
res = count(n)
for i in res:
    print(i)