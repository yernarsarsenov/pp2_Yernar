n = int(input())
a = map(str, input().split())
print(max(a, key=len))