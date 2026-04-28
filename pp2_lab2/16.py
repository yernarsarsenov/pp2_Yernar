n = int(input())
arr = list(map(int, input().split()))
s = set()
for i in arr:
    if i in s:
        print("NO")
    else:
        print("YES")
    s.add(i)