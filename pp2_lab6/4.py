n = int(input())
a = map(int, input().split())
b = map(int, input().split())
print(sum(i * j for i, j in zip(a, b)))