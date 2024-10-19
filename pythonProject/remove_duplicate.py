nums  = [-9,-2,0,2,3]
output = [0,4,4,9,81]
map = list(map(lambda x:x*x,nums))
print(sorted(map))


# def removeDuplicates(nums):
#     if not nums:
#         return 0
#     unique_index = 1
#     for i in range(1, len(nums)):
#         if nums[i] != nums[i - 1]:
#             nums[unique_index] = nums[i]
#             unique_index += 1
#     return unique_index


# nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
# k2 = removeDuplicates(nums2)
# print(k2, nums2[:k2])  # Output: 5 [0, 1, 2, 3, 4]


