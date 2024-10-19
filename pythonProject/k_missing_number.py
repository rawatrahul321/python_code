s = [1,2,3,1,2,3,4,5,6,1,2,3]
result = [1,2,3]
result1= []
for i in s:
   if i not in result1:
      result1.append(i)
print(result1)


# def solve(nums, k):
#    nums = set(nums)
#    count = 0
#    num = 1
#    while count < k:
#       if num not in nums:
#          count += 1
#       if count == k:
#          return num
#       num += 1
#    return num
#
# nums = [1,2,4,8,12]
# k = 6
# print(solve(nums, k))