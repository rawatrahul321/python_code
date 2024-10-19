nums =  [2, 4, -1, 1,5]
def firstMissingPositve(nums):
    if nums == []:
        return 1
    else:
        a = max(nums)
        for i in range(1 , a+2):
            if i not in nums:
                c = i
                return c
print(firstMissingPositve(nums))