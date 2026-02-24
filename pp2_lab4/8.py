def primes(n):
    if n == 0:
        return None
    prime = [True for _ in range(n + 1)]
    prime[0] = prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if prime[i]:
            for j in range(i * i, n + 1, i):
                prime[j] = False
    for i in range(2, n + 1):
        if prime[i]:
            yield i
n = int(input())
res = primes(n)
for i in res:
    print(i, end=' ')