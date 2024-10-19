
# nums = [4,1,2,1,2]
# def single_number(nums):
#     d = {}
#     for i in nums:
#         if i not in d:
#             d[i]=1
#         else:
#             d[i]+=1
#     for i in nums:
#         if d[i]==1:
#             return i
# print(single_number(nums))


# string1 = 'loveleetcode'
# def first_single_char(string1):
#     d = list(string1)
#     dq = {}
#     for i in string1:
#         if i not in dq:
#             dq[i]=True
#         else:
#             dq[i]=False
#     for i,c in enumerate(string1):
#         if dq[c]:
#             return i
# print(first_single_char(string1))

# Revserse String

# arr = ['h','e','l','l','o']
# left,right=0,len(arr)-1
# while left<right:
#     arr[left],arr[right]=arr[right],arr[left]
#     left+=1
#     right-=1
# print(arr)

# nums = [0,1,0,3,12]
# def last_zero(nums):
#     prev = 0
#     for i in range(len(nums)):
#         if nums[i]!=0:
#             nums[prev],nums[i]=nums[i],nums[prev]
#             prev+=1
#     return nums
# print(last_zero(nums))

