n = int(input())
count = dict()
temp = 0
for i in range(n):
    a = input()
    if a in count:
        count[a] += 1
    else:
       count[a] = 1
for i in count:
    if count[i] == 3:
            temp += 1
print(temp)