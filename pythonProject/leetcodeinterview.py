#kadane's Algorithm
def max_Subarray_Sum(my_array, array_size):
    maxTillNow = my_array[0]
    maxEnding = 0
    for n in range(0, array_size):
        maxEnding = maxEnding + my_array[n]
        if maxEnding < 0:
            maxEnding = 0

        elif (maxTillNow < maxEnding):
            maxTillNow = maxEnding

    return maxTillNow


my_array = [-2, -3, 4, -1, -2, 5, -3]
print(max_Subarray_Sum(my_array, len(my_array)))


# n = [3,-1,-2,-5,2,-4,4,7]
# output = [3, -1, 2, -2, 4, -5, 7, -4]
# p = []
# ne = []
# for i in n:
#     if i>0:
#         p.append(i)
#     else:
#         ne.append(i)
# print(p)
# print(ne)
# cons = []
# for i,j in zip(p,ne):
#     cons.append(i)
#     cons.append(j)
# print(cons)

# nums  = [5,2,6,1,1]
# output = [2,1,1,0]
# li = []
# l = []
# n = len(nums)
# for i in range(len(nums)):
#     for j in range(i+1,len(nums)):
#         if nums[i]<nums[j]:
#             li.append(nums[i])
#             print(nums[i],nums[j])
# print(li)

# my_nums = [0,15,68,1,0,-55]
# def get_largest(nums):
#     largest = nums[0]
#     for num in nums:
#         if num>largest:
#             largest = num
#     return largest
# print(get_largest(my_nums))
#
# my_nums = [0,15,68,45,69]
# def get_second_largest(nums):
#     largest = nums[0]
#     second_largest = nums[0]
#     for i in range(1,len(nums)):
#         if nums[i]>largest:
#             second_largest = largest
#             largest = nums[i]
#         elif nums[i]>second_largest:
#             second_largest = nums[i]
#     return second_largest
# print(get_second_largest(my_nums))


# numbers = [2,3,4]
# target = 6
# def twosum(numbers):
#     for i in range(len(numbers)):
#         for j in range(i+1,len(numbers)):
#             if numbers[i]+numbers[j]==target:
#                 return [j+1,i+1]
# print(twosum(numbers))

# s = "ab"
# t = "baab"
# def isSubsequence(t):
#     i, j = 0, 0
#
#     while i < len(s) and j < len(t):
#         if s[i] == t[j]:
#             i += 1
#         j += 1
#
#     return i,s
#
# print(isSubsequence(t))
# nums = [0,0,1,1,1,2,2,3,3,4]
# val = 2
# print(nums[:])
# def remove_element(nums):
#     if not nums:
#         return 0
#     unique_index = 1
#     for i in range(1, len(nums)):
#         if nums[i] != nums[i - 1]:
#             nums[unique_index] = nums[i]
#             unique_index += 1
#     return unique_index,nums[:unique_index]
#     # l = []
#     # for i in nums:
#     #     if i not in l:
#     #         l.append(i)
#     # return len(l),l
# print(remove_element(nums))
