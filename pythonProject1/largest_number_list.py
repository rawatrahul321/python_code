# from functools import cmp_to_key
# numbers = [4, 1, 7, 2, 9, 3]
# def compare(a,b):
#     return a-b
# number = sorted(numbers,key=cmp_to_key(compare))
# print(number)

# nums = [3,30,34,5,9]
# def largest_num(nums):
#     for i,n in enumerate(nums):
#         nums[i]=str(n)
#     def compare(n1,n2):
#         if n1+n2>n2+n1:
#             return -1
#         else:
#             return 1
#     nums = sorted(nums,key=cmp_to_key(compare))
#     return str(int("".join(nums)))
# print(largest_num(nums))

# nums = [4,3,2,7,8,2,3,1]
# nums = [1,2,2,8]
# li = []
# for i in range(1,max(nums)):
#     if i not in nums:
#         li.append(i)
# print(li)

nums = [1,2,3,3,3,2,1,3]
# def majority_element(nums):
#     d = {}
#     res,maxCount=0,0
#     for i in nums:
#         d[i]=d.get(i,0)+1
#         print(d)
#         if d[i]>maxCount:
#             res  = i
#         maxCount = max(d[i],maxCount)
#     return res
# print(majority_element(nums))
# nums = [1,2,3,4,3,3]
# def majority(nums):
#     res,count=0,0
#     for i in nums:
#         if count==0:
#             res = i
#         if i==res:
#             count+=1
#         else:
#             count-=1
#     return res,count
# print(majority(nums))

nums  = [1,2,3,4,1,2,3,3]
print(dir(nums))
s = set(i for i in nums if nums.count(i)>1)
print(list(s))