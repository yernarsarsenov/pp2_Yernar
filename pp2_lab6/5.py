s = input()
vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
print("Yes" if any(ch in vowels for ch in s) else "No")