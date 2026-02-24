def limited_cycle(n, k):
    for i in range(k):
        yield n
n = list(input().split())
k = int(input())
res = limited_cycle(n, k)
for i in res:
    print(*i, end=" ")