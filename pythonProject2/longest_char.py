s = "He I like Cookies"
sq = s.split()
largest = ''
for i in range(len(sq)):
    if len(largest) < len(sq[i]):
        largest = sq[i]
print(largest)
# def find_longest_word(word_list):
#     longest_word = ''
#     for word in word_list:
#         if len(word) > len(longest_word):
#             longest_word = word
#     return longest_word
# print(find_longest_word(s.split()))

# word = ''
# maxWord = ''
# l = []
# s1 = s.split()
# for i in s1:
#     if len(i) > len(word):
#         maxWord = word
#     # else:
#     #     word = i
# print ("Longest word:", maxWord)
# print ("Length:", len(maxWord))   


# a = "jayyyyyyyyyyyyyyyi"
# count = 0
# maxcount = 0
# lastCharacter = ""
# longestcharacter = ""
# for ch in a:
#     if(ch == lastCharacter):
#         count += 1
#         if(count > maxcount):
#             maxcount = count
#             longestcharacter = ch
#     else:
#         count = 1
#         lastCharacter = ch
# print(longestcharacter)
# print(maxcount)

s = 'jayyiiiaaaa'
maxcount = 0
char  = s[0]
current  = 1
for i in range(1,len(s)):
    if s[i]==s[i-1]:
        current +=1
    else:
        maxcount = max(maxcount,current)
        current = 1
maxcount = max(maxcount,current)
print(maxcount)

