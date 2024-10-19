# def isAnagram(str1, str2):
#     if len(str1) != len(str2):
#         return False
#     feq_map = {}
#     for ch in str1:
#         if ch in feq_map:
#             feq_map[ch] += 1
#         else:
#             feq_map[ch] = 1
#     for ch in str2:
#         if ch not in feq_map or feq_map[ch] == 0:
#             return False
#         else:
#             feq_map[ch] -= 1
#     return True
#
#
# print(isAnagram("israhul", "rahulis2"))

# def pair_of_elementttts(nums,target):
#     number_seen = {}
#     for arr in nums:
#         diff = target - arr
#         if diff in number_seen:
#             print([arr,diff])
#         number_seen[arr] = True
#     print(number_seen)
# print(pair_of_elementttts((4,7,8,1,3,2,44),9))

# findmin = [13,16,17,19,3,4,8,9]
# left = 0
# right = len(findmin)-1
# while left<right:
#     mid = (left+right)//2
#     print(mid,findmin[mid],"PPWOO")
#     if findmin[mid]>findmin[right]:
#         left = mid+1
#     else:
#         right = mid
# print(findmin[left])

# # tWO pOINTTER tECHNIIQUE
#
# num = [-9,-4,-1,1,2,3,4,6]
# s = 0
# l = len(num) - 1
# while s<l:
#     sum = num[s]+num[l]
#     if sum==0:
#         print([num[s],num[l]])
#         break
#     elif sum<0:
#         s =s+1
#     else:
#         l=l-1

# nums = [11,22,33,44,55]
# low,high = 0,len(nums)-1
# target = 55
# while low<=high:
#     if nums[low]+nums[high]==target:
#         print ([nums[low],nums[high]])
#         break
#     elif nums[low]+nums[high]<target:
#         low=low+1
#     else:
#         high-=1

# def quick_sort(arr):
#     if len(arr)<=1:
#         return arr
#     else:
#         pivot = arr[0]
#         left = [x for x in arr[1:] if x < pivot]
#         right = [x for x in arr[1:] if x >= pivot]
#         return quick_sort(left) + [pivot] + quick_sort(right)
# print(quick_sort([3,43,54,534,52354,1425,345,34532,32,23,2,33]))
# def factorial(x):
#     if x == 1:
#         return 1
#     else:
#         return x* factorial(x - 1)
# print(factorial(5))

# def find_factorial(x):
#     factorial = 1
#     for i in range(1,x+1):
#         factorial = factorial * i
#     print (factorial)
# find_factorial(5)

qsort = lambda l:l if len(l)<=1 else qsort([x for x in l[1:] if x<l[0]]) + [(l[0])] + qsort([x for x in l[1:] if x>=l[0]])
print(qsort([66,4,2,77,33]))