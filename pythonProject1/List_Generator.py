arr  = [44,33,55,66,22]
for i in range(len(arr)):
    for j in range(i+1,len(arr)):
        if arr[i]>arr[j]:
            arr[i],arr[j]=arr[j],arr[i]
print(arr)
# s= "hello"
# vowels = 'aeiou'
# s = list(s)
# i, j = 0, len(s) - 1
# while i < j:
#     if s[i] not in vowels:
#         i += 1
#     elif s[j] not in vowels:
#         j -= 1
#     else:
#         s[i], s[j] = s[j], s[i]
#         i += 1
#         j -= 1
# print(''.join(s))


# li = [1,2,3,55,4]
# li1 = [33,4,2,22]
# s = set(li)&set(li1)
# print(s)
#
# gen_exp = (x ** 2 for x in range(10) if x % 2 == 0)
# print(list(gen_exp))
#
# a = 'ab'
# b = 'pqr'
# out = ''
# inlen = min(len(a),len(b))
# for i,j in zip(a,b):
#     out+=i
#     out+=j
# out+=a[inlen:]
# out+=b[inlen:]
# print(out)