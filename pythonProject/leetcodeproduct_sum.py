s = "pwwkew"
count = 0
max_length = 0
start = 0
char_index = {}

for i in range(len(s)):
    if s[i] in char_index and char_index[s[i]] >= start:
        start = char_index[s[i]] + 1
        print(char_index,s[i])

    char_index[s[i]] = i
    count = max(count, i - start + 1)

print(count)

# nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
# # print(sum(nums))
# def longest_sum(nums):
#     current = nums[0]
#     max_current = nums[0]
#     for i in nums[1:]:
#         print(i)
#         current = max(current+i,i)
#         max_current = max(max_current,current)
#         print(max_current,current)
#     return max_current,current
# print(longest_sum(nums))

# nums = [3,2,4]
# target = 6
# for i in range(len(nums)):
#     for j in range(i+1):
#         # print(nums[i],nums[j])
#         if nums[i]+nums[j]==target and i!=j:
#             print(nums[i]+nums[j])
#             print([j,i])


# words = ["the","day","is","sunny","the","the","the","sunny","is","is","lll"]
# k = 4
# Output = ["the","is","sunny","day"]
# words =["i","love","leetcode","i","love","coding"]
# k =3
# def longest_word_first(words):
#     d = {}
#     for i in words:
#         d[i]=d.get(i,0)+1
#     l = list(d)
#     # print(l)
#     # print(d)
#     l1 = []
#     sorted_keys = sorted(d.keys(), key=lambda x: (-d[x], x))
#     result_list = list(sorted_keys)
#
#     return (result_list[:k])
# print(longest_word_first(words))


# def longest_word_first(words):
#     d = {}
#     for i in words:
#         d[i]=d.get(i,0)+1
#     l = list(d)
#     # print(l)
#     print(d)
#     l1 = []
#     sorted_list = sorted(d.items(), key=lambda x: x[1], reverse=True)
#     result_list = [word for word, count in sorted_list]
#
#     return (result_list[:k])
# print(longest_word_first(words))

# def isValid( s):
#     stack = []
#     lookup = {"(": ")", "{": "}", "[": "]"}
#     for parenthese in s:
#         if parenthese in lookup:
#             stack.append(parenthese)
#             print(stack)
#         elif len(stack) == 0 or lookup[stack.pop()] != parenthese:
#             return False
#     return len(stack) == 0
# # print(isValid("(]"))
# print(isValid(("()[{}]{}")))

# dictionary = ["cat","bat","rat"]
# sentence = "the cattle was rattled by the battery"
# Output = "the cat was rat by the bat"
# li = sentence.split()
# list1  = []
# for char in li:
#     if char[:len(dictionary[0])] in dictionary:
#         list1.append(char.replace(char[len(dictionary[0]):],''))
#     else:
#         list1.append((char))
# print(' '.join(list1))






# s = "cattle"
# d = "cat"
# l = len(d)
# sp = s[l:]
# print(s.replace(sp,""))
# n = 234
# def product_sum(n):
#     m = list(map(int,str(n)))
#     s  = 1
#     d = 0
#     for i in m:
#         s*=i
#         d+=i
#     f = s-d
#     return s-d
# print(product_sum(n))
