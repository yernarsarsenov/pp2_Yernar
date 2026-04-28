#even numbers generator
def evens(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
res = evens(n)
for i in res:
    if i == n or i == n - 1:
        print(i, end="")
    else:
        print(i, end=",")