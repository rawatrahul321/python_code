words = ['mass','as','hero','superhero']
output = ['as','hero']
out = []
s = words.sort(key=len)
print(words)
for i in range(len(words)):
    word = words[i]
    for j in range(i+1,len(words)):
        other_words = words[j]
        print(word,other_words)
        if word in other_words:
            out.append(word)
            break
print(out)   

words = ['flower','flow','float']
prefix = words[0]
for word in words[1:]:
    prefix = words[0]
    while not word.startswith(prefix):
        prefix = prefix[:-1]
        if not prefix:
            break
print(prefix) 

# def longest_no_repeating_char(s):
#     charSet = set()
#     l = 0
#     res = 0
#     for r in range(len(s)):
#         while s[r] in charSet:
#             charSet.remove(s[l])
#             print(charSet, "charSet")
#             l += 1
#         charSet.add(s[r])
#         res = max(res, r - l + 1)
#     return res


# print(longest_no_repeating_char("abcabccbb"))

# nums = [1,2]
#
# t = 2
# def count2sum(nums,t):
#     d  = {}
#     for i in nums:
#         d[i]=d.get(i,0)+1
#     l = []
#     print(d)
#     for k,v in d.items():
#         if v>=t:
#             l.append(k)
#     return l
# print(count2sum(nums,t))


# def subarraysum(nums,k):
#     res = 0
#     curSum = 0
#     preFixSum = {0:1}
#     for n in nums:
#         curSum+=n
#         diff = curSum - k
#         res+=preFixSum.get(diff,0)
#         preFixSum[curSum]= preFixSum.get(curSum,0)+1
#     return  res
# print(subarraysum([1,-1,1,1,1,1],3))



# Longest Palindrome Substring
# def longest_palindrome_substring(s):
#     res = ''
#     resLen = 0
#     for i in range(len(s)):
#         l ,r = i,i
#         while l>=0 and r< len(s) and s[l]==s[r]:
#             if (r-l+1) > resLen:
#                 res = s[l:r+1]
#                 resLen = r - l +1
#             l-=1
#             r+=1
#         l,r=i,i+1
#         while l>=0 and r< len(s) and s[l]==s[r]:
#             if (r-l+1) > resLen:
#                 res = s[l:r+1]
#                 resLen = r - l +1
#             l-=1
#             r+=1
#     return res
# print(longest_palindrome_substring('babad'))
# Palindrome Substrings
# def palindrome_substring(s):
#     res = 0
#     for i in range(len(s)):
#         l = r  = i
#         while l>=0 and r < len(s) and s[l]==s[r]:
#             res+=1
#             l-=1
#             r+=1
#         l = i
#         r = i+1
#         while l>=0 and r < len(s) and s[l]==s[r]:
#             res+=1
#             l-=1
#             r+=1
#     return res
# print(palindrome_substring(('aaab')))
# nums  = [0,1]
# def missing_number(nums):
#     res  = len(nums)
#     for i in range(len(nums)):
#         res = res + (i - nums[i])
#     return res
# print(missing_number(nums))

# nums = [-2,1,-3,4,-1,2,1,-5,4]
# def max_subaarrar(nums):
#     maxSub = nums[0]
#     curSub = 0
#     for n in nums:
#         if curSub < 0:
#             curSub = 0
#         curSub+=n
#         maxSub = max(maxSub,curSub)
#     return maxSub
# print(max_subaarrar(nums))

#Product of Array Except self

# nums = [1,2,3,4]
# output = [24,12,8,6]
# n = len(nums)
# ans = [1] * n
#
# # Use ans as the prefix product array.
# for i in range(1, n):
#   ans[i] = ans[i - 1] * nums[i - 1]
#   print(ans)
# suffix = 1  # suffix product
# for i, num in reversed(list(enumerate(nums))):
#   ans[i] *= suffix
#   suffix *= num
#
# print( ans)

# nums = [1,2,3,4]
# output = [24,12,8,6]
# n = len(nums)
# prefix = [1] * n  # prefix product
# suffix = [1] * n  # suffix product
#
# for i in range(1, n):
#   prefix[i] = prefix[i - 1] * nums[i - 1]
#
# for i in reversed(range(n - 1)):
#     suffix[i] = suffix[i + 1] * nums[i + 1]
#
# print([prefix[i] * suffix[i] for i in range(n)])