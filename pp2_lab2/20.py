n = int(input())
d = dict()

for i in range(n):
    com = input().split()

    if com[0] == "set":
        key = com[1]
        value = com[2]
        d[key] = value

    else:
        key = com[1]
        if com[1] in d:
            print(d[key])
        else:
            print(f"KE: no key {key} found in the document")