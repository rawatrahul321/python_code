# def array(arr):
#     for i in range(len(arr)-2):
#         if arr[i]==1 and arr[i+1]==2 and arr[i+2]==3:
#             return True
#     else:
#         return False
# print(array([1,5,3, 2, 3, 1]))

# output = 'CCoCodCode'
# def string_splosion(s):
#     d = ''
#     for i in range(len(s)):
#         d = d + s[:i+1]
#     return d
# print(string_splosion('Code'))
# n = "fun&!! time"
# Output = 'time'
# current_max = 0
# import re
# d = re.findall("\w+", n)
# print(max(d))

# def count_hi(s):
#     count = 0 
#     for i in range(len(s)):
#         if s[i]=='h' and s[i+1]=='i':
#             count+=1
#     return count
# print(count_hi('ABChi hi'))
# double_char('Hi-There') → 'HHii--TThheerree'
# def double_char(s):
#     d = ''
#     for i in range(len(s)):
#        d = d + s[i]+s[i]
#     return d
# print(double_char('Hi-There'))

#lone_sum(1, 2, 3) → 6
#lone_sum(3, 2, 3) → 2
#lone_sum(3, 3, 3) → 0
# def lone_sum(a, b, c):
#   sum = 0
#   if a != b and a != c: 
#     sum += a
#   if b != a and b != c: 
#     sum += b
#   if c != a and c != b: 
#     sum += c
  
#   return sum
# def lone_sum(a,b,c):
#     d = [a,b,c]
#     dict = {}
#     for i in d:
#         dict[i]=dict.get(i,0)+1
#     l = []
#     for k,v in dict.items():
#         if v<2:
#             l.append(k)
#     return sum(l)
# print(lone_sum(1,2,3))
# print(lone_sum(3,2,3))
# print(lone_sum(3,3,3))
# n = 'a3b3c2a2'
# l = ''
# for i in n:
#     if i.isalpha():
#         f = i
#     else:
#         l = l + f * int(i)
# print(l)

# def process_string(source):
#     new = ''
#     while source:
#         counter = 0
#         first_char = source[0]
#         while source and source[0] == first_char:
#             counter += 1
#             source = source[1:]
#         new = new + first_char + str(counter)
#     return new

# print(process_string('aaabbbccaa'))
# 'a3b3c2a2'

s ='a3b3c2a2'
output = ''
f = 1
char  = s[0]
for i in s:
    if not i.isdigit():       
        char  = i
    else:
        f = i
        output = output +  str(char)*  int(f)
print(output)
output = 'aaabbbccaa'
