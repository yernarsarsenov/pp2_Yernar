n = int(input())
nums = list(map(int, input().split()))
d = {}

for i in nums:
    d[i] = d.get(i, 0) + 1
max_freq = max(d.values())

res = min(i for i, j in d.items() if j == max_freq)
print(res)