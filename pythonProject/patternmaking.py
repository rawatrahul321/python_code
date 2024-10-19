n = 4
for i in range(n,0,-1):
    for j in range(n-i):
        print(" ",end=" ")
    for k in range(1,2*i):
        print("*",end=" ")
    print()
for i in range(2,n+1):
    for j in range(n-i):
        print(" ",end=" ")
    for k in range(1,2*i):
        print("*",end=" ")
    print()


# n = 4
# num = 1
# next_num = 2
# for i in range(n+1):
#     for j in range(i):
#         print(num,end= " ")
#         temp = next_num
#         next_num = next_num + num
#         num = temp
#     print()

# d = {'d':3,'f':2,'e':4,'b':1,'a':1}
# sorted_d = sorted(d.keys(),key=lambda x:(-d[x],x))
# print(sorted_d)
#
# n = 5
# for i in range(0,1):
#     print(i)

# n=5
# for i in range(1, n + 1):
#     num = i
#     for j in range(1, i + 1):
#         print(num, end=" ")
#         num = num + n - j
#
#     print()
# for i in range(n):
#     for j in range(i+1):
#         x = 0
#         for k in range(j):
#             x = x +n -k
#
#         if j%2==0:
#             # print("*",end=" ")
#             print(x+i-j+1,end=" ")
#         else:
#             print(x+n-i,end=" ")
#     print()

