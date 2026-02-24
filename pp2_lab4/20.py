#scope accumulator
g = 0
n = 0

m = int(input())
for _ in range(m):
    mode, val = input().split()
    val = int(val)
    
    if mode == "global":
        g += val
    elif mode == "nonlocal":
        n += val

print(g, n)