n =5
for i in range(n+1):
    for j in range(i):
        if j==0 or i==n or j==i-1:
            print("*",end= " ")
        else:
            print(" ",end=" ")
    print()

n = int(input("Number:"))
for i in range(1,n+1):
    for j in range(1,2*n):
        if (i==n and j%2!=0) or i+j==n+1 or j-i==n-1:
            print("*",end=" ")
        else:
            print(" ",end=" ")
    print()

# n = 10
# for i in range(n, 0, -1):
#     for j in range(i):
#         if j == 0 or i == n:
#             print("*", end="")
#         elif j == i - 1:
#             print("*", end="")
#         else:
#             print(" ", end="")
#     print()
# n = 10
# for i in range(n,0,-1):
#     for j in range(i,0,-1):
#         print(' ',end="")
#     for j in range(2*(n-i)+1):
#         if j==0 or j==2*(n-i):
#             print("*",end="")
#         elif i==1:
#             print("*",end="")
#         else:
#             print(" ",end="")
#     for j in range(i,0,-1):
#         print(' ',end="")
#     print()

# n=5
# for i in range(n+1):
#     for j in range(i):
#         print(ord(i),end=" ")
#     print()
# n = 5
# for i in range(n,0,-1):
#     for j in range(i,0,-1):
#         print("*",end=" ")
#     for j in range(2*(n-i)):
#         print(" ",end=" ")
#     for j in range(i,0,-1):
#         print("*",end=" ")
#     print()