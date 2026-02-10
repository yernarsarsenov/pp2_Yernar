n = int(input())
att = set()
while n > 0:
    name = input()
    att.add(name)
    n -= 1
print(len(att))