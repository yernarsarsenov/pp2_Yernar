n = int(input())
nums = list(map(int, input().split()))
print(nums.index(max(nums)) + 1)