def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        yield a
        b, a = a + b, b
n = int(input())
res = list(fibonacci(n))
print(','.join(map(str, res)))