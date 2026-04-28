def isValid(n):
    valid = False
    while n > 0:
        if (n % 10) % 2 == 0:
            valid = True
        else:
            return False
        n //= 10
    return valid
n = int(input())
print("Valid" if isValid(n) else "Not valid")