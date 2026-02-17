n = int(input())

def is_usual(num):
    
    while num % 2 == 0:
        num //= 2
    while num % 3 == 0:
        num //= 3
    while num % 5 == 0:
        num //= 5
    
    return num == 1

print("Yes" if is_usual(n) else "No")