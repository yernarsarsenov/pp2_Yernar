def power_of_two(n):
    for i in range(n + 1):
        yield 2 ** i
n = int(input())
res = power_of_two(n)
for i in res:
    print(i, end=" ")