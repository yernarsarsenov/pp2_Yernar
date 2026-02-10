n = int(input())
print(len([i for i in list(map(int, input().split())) if i > 0]))