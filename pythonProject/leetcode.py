# longest common sequences

# text1  = 'abcdef'
# text2 = 'ace'
# dp = [[0 for j in range(len(text2)+1)]  for i in range(len(text1)+1)]
# print(dp)
# for i in range(len(text1)-1,-1,-1):
#     for j in range(len(text2)-1,-1,-1):
#         if text1[i]==text2[j]:
#             dp[i][j] = 1+dp[i+1] [j+1]
#         else:
#             dp[i][j] = max(dp[i][j+1],dp[i+1][j])
# print(dp[0][0])

# missing Number
#
# n = [3,0,1,2,5,6,4,8]
# l = len(n)
# d  = l*(l+1)/2
# print(d-sum(n))

# num = [5,8,2,3,1,4]
#
# def longest_success_element(num):
#     a_set = set(num)
#     higest_sequence = 0
#     for i in a_set:
#         if i-1 not in a_set:
#             count = 0
#             num = i
#             while num in a_set:
#                 count+=1
#                 num+=1
#             if higest_sequence<count:
#                 higest_sequence = count
#     return higest_sequence
# print(longest_success_element(num))

# Longest Consecutive Number
# def longest_consective_sorted_array(nums):
#     numSet = set(nums)
#     longest  = 0
#     for n in nums:
#         if (n-1) not in numSet:
#             length = 0
#             while (n+length) in numSet:
#                 length+=1
#             longest = max(longest,length)
#     return longest
# print(longest_consective_sorted_array([100,3,200,1,2,4]))

# # longest increasing element
#
# n = [5,6,7,8,3,2,1,2,4]
# l = []
# for i in range(len(n)):
#     l.append(1)
#     for j in range(i):
#         if n[i]>n[j]:
#             l[i]=max(l[i],l[j]+1)
#     print(l)
#     print(max(l) if l else 0)

# nums = [2,2,2,2,2,2]
# LIS = [1]*len(nums)
# for i in range(len(nums)):
#     for j in range(i):
#         if nums[i]>nums[j]:
#             LIS[i]=max(LIS[i],1+LIS[j])
# print(max(LIS))
# print(LIS)

# best time to buy and sell
# num = [7,1,5,3,4,6]
#
#
# def buy_sell(num):
#     buy = num[0]
#     max_profit = 0
#     for i in range(1,len(num)):
#         if buy>num[i]:
#             buy = num[i]
#         elif num[i]-buy>max_profit:
#             max_profit= num[i]-buy
#     return max_profit
# print(buy_sell(num))

# num = 587
# def sum_of_num(num):
#     sum = 0
#     while num > 0:
#         sum += num % 10
#         num = num // 10
#         if num == 0 and sum > 9:
#             num = sum
#             sum = 0
#     return sum
# print(sum_of_num(num))

# def isPerfectSquare(num):
#     left, right = 1, num
#     while left <= right:
#         mid = (left + right) // 2
#         perfect = mid * mid
#         if perfect == num:
#             return mid
#         elif perfect < num:
#             left = mid + 1
#         else:
#             right = mid - 1
#     return False
# print(isPerfectSquare(16))

# nums = [1,3,5,6]
# target = 7
# def searchInsert(nums):
#     left, right = 0, len(nums) - 1
#
#     while left <= right:
#         mid = left + (right - left) // 2
#
#         if nums[mid] == target:
#             return mid
#         elif nums[mid]>target:
#             right = mid-1
#         else:
#             left = mid+1
#     return left

# def searchInsert(nums):
#     for i in range(len(nums)):
#         if target==nums[i]:
#             return i
#         elif target<nums[i]:
#             return i
#     return len(nums)
#
# print(searchInsert(nums))

# def missing_number(nums):
#     s = len(nums) + 1
#     n = s * (s + 1) // 2
#     actual_s = sum(nums)
#     print(actual_s, n, s)
#     return n-actual_s
# print(missing_number(nums))

# nums = [4,1,2,1,2]
# def single_number(nums):
#     d = {}
#     for i in nums:
#         d[i]=d.get(i,0)+1
#     for k,v in d:
#         if len(k)>1 and v==1:
#             return k
#     else:
#         return 1

# digits = [4,32,1]
# l = []
# def plus_one(digits):
#     I = [(str(digit)) for digit in digits]
#     p = ''.join((I))
#     p1 = int(p) + 1
#     d = []
#     for i in list(str(p1)):
#         d.append(int(i))
#     return d
# print(plus_one((digits)))

# x = 123
# l = list(str(x))
# print(l)
# def rev_num(x):
#     s = []
#     for i in range(len(l)-1,-1,-1):
#         s.append(str(l[i]))
#     print(s)
#     return ''.join(s)
# print(rev_num(x))

# s = "the sky is blue"
# o = "blue is sky the"
# def rev(s):
#     l = s.split()
#     l1 = []
#     print(l)
#     for i in range(len(l)-1,-1,-1):
#         l1.append(l[i])
#     return ' '.join(l1)
# print(rev(s))


# nums = [1,2,3,1]
# def duplicate_number(nums):
#     d = {}
#     for i in nums:
#         d[i]=d.get(i,0)+1
#     for k,v in d.items():
#         if v==2:
#             return True
#     else:
#         return False
# print(duplicate_number((nums)))

# def first_non_repeating_char(string):
#     dict = {}
#     size = len(string)
#     for i in range(size):
#         key = string[i]
#         if key not in dict:
#             dict[key] = 1
#         else:
#             dict[key] = dict[key] + 1
#     for key,value in dict.items():
#         if value==1:
#             print(key,value)
#             break
# first_non_repeating_char('pwwkew')