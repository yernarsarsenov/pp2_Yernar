n = int(input())
nums = list(map(int, input().split()))
min = min(nums)
max = max(nums)
for i in range(len(nums)):
    if nums[i] == max:
        nums[i] = min
print(*nums) 