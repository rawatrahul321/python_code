# Largest string count between two char in string

a = 'abcduuubca'
char_index  = {}
res = -1
for i,j in enumerate(a):
    if j in char_index:
        res  = max(res,i-char_index[j]-1)
    else:
        char_index[j] = i
print(res)

# li = ['lock','cool','cock']
# output = ['c','o']
# common  = set(li[0])
# for i in li[1:]:
#     common &= set(i)
# print(list(common))

# d1 = ['a','b','c']
# d2 = [11,33,22]
# h = {}
# for i,j in zip(d2,d1):
#     h[i] = j
# print(h)
# res = []
# for i in (sorted(d2)):
#     res.append(h[i])
# print(res)


# from collections import defaultdict
#
# str1 = 'the apple is sweet'
# str2 = 'the apple is sour'
# res  = []
# li = defaultdict(int)
# for w in str1.split(" ") + str2.split(" "):
#     li[w] +=1
# for w,count in li.items():
#     if count==1:
#         res.append(w)
# print(res)


# arr = [21,2,44,33,32,11231]
# def insertion_sort(arr):
#     for i in range(len(arr)):
#         j = i
#         while j>0 and arr[j]<arr[j-1]:
#             arr[j-1],arr[j]=arr[j],arr[j-1]
#             j-=1
#         print(arr)
#     print(arr)
# insertion_sort(arr)


# def fact(n):
#     if n==1:
#         return 1
#     else:
#         return n*fact(n-1)
# print(fact(5))

# def fibo(n):
#     if n<=1:
#         return n
#     else:
#         return fibo(n-1)+fibo(n-2)
#
# for i in range(10):
#     print(fibo(i),end=" ")

# def armstronng(n):
#     li = [int(i)**len(str(n)) for i in str(n)]
#     return sum(li)==n
# print(armstronng(372))

# s = 'rahulrawat'
# print(s[2:8:-2])


# import random
# for i in range(10):
#     print(random.uniform(99,100),end=" ")

# nums = [22,4,4,33,22]
# num = iter(nums)
# while True:
#     try:
#         n = next(num)
#         print(n)
#     except StopIteration:
#         break