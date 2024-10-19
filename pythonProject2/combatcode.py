# def make_ends(nums):
#     l = []
#     l.append(nums[0])
#     l.append(nums[-1])
#     return l
# print(make_ends([7, 4, 6, 2]))
# def has22(nums):
#     for i in range(len(nums)-1):
#         if nums[i]==2 and nums[i+1]==2:
#             return True
#     else:
#         return False
# print(has22([1, 2, 2]))
# def sum67(nums):
#     total = 0
#     found6 = False
      
#     for i in range(len(nums)):
#         if nums[i] == 6:
#             found6 = True
#         if not found6:
#             total += nums[i]
#         if nums[i] == 7 and found6:
#             found6 = False
            
#     return total
# print(sum67([1, 6, 2, 2, 7, 1, 6, 99, 99, 7]))
# print(sum67([2, 7, 6, 2, 6, 2, 7]))

# def sum67(nums):
#     while 6 in nums:
#         index_6 = nums.index(6)
#         if 7 in nums[index_6:]:
#             index_7 = nums.index(7, index_6)
#             print(index_6,index_7,nums,nums[index_6:])
#             del nums[index_6:index_7+1]
#         else:
#             break

#     return sum(nums)

# print(sum67([1, 6, 2, 2, 7, 1, 6, 99, 99, 7]))
# print(sum67([2, 7, 6, 2, 6, 2, 7]))

# def sum67(nums):
#     nums_new = nums[nums.index(6):nums.index(7)+1]
#     l1 = nums
#     l2 = set(nums_new)
#     lu = list(filter(lambda x: x not in l2, l1))
#     print(lu)
#     return sum(lu)

# print(sum67([1, 2, 2, 6, 99, 99, 7])) 

# def sum13(nums):
#     count = 0
#     d =0 
#     while d<len(nums):
#         if nums[d]==13:
#             d+=2
#         else:
#             count+=nums[d]
#             d+=1
#     return count
# # print(sum13([1, 2, 2, 1, 13]))
# print(sum13([1, 2, 13, 2, 1, 13]))
