n, l, r = map(int, input().split())
nums = list(map(int, input().split()))
print(*nums[0: l - 1], *((nums)[l - 1:r])[::-1], *nums[r: n])