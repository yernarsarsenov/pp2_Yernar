x = int(input())

if x < 2:
    print("No")
else:
    is_prime = True
    for i in range(2, int(x**0.5) + 1):
        if x % i == 0:
            is_prime = False
            break
    if is_prime:
        print("Yes")
    else: 
        print("No")
