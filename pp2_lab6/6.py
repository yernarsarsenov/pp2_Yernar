n = int(input())
a = map(int, input().split())
print("Yes" if all(n >= 0 for n in a) else "No")