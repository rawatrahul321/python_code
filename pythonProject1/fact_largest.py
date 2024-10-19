# def first_uniq_char(s):
#   feq = {}
#   for i in s:
#     feq[i] = feq.get(i, 0) + 1
#   for i, char in enumerate(s):
#     if feq[char] == 1:
#       return char
#   return -1
# print(first_uniq_char('dhhdhaksdasasas'))
nums = [5, 2, 1,3, 4, 6]

nums = [1,3,5,6]
def missing_number(nums):
  s = len(nums) + 1
  n = s * (s + 1) // 2
  actual_s = sum(nums)
  print(actual_s,n,s)
  if n-actual_s==0:
    return nums[-1]+1
  else:
    return n - actual_s


print(missing_number(nums))

# l = 203
# r = str(l).split('0')
# print(''.join(r))

# lst1 = [1, 2, 3, 4, 5]
# lst2=[]
# for i in lst1:
#   lst2.insert(0,i)
#   print(lst2)

# def fact(n):
#     if n==1:
#         return n
#     else:
#         return n*fact(n-1)
# print(fact(6))