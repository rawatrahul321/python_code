# n = 5
# for i in range(n):
#     if i == 0 or i == n - 1:
#         print(n * '*')
#     else:
#         print('*' + (n - 2) * '  ' + '*')
# for i in range(n):
#     if i==n-1:
#         print(n*'*')
#     else:
#         print(1*"*"+i*'  '+ '*'*1)
#     for j in range(i):
#         print(i,end=" ")
#     print()
# for i in range(n-1,0,-1):
#     for j in range(i):
#         print(i,end=" ")
#     print()
# for i in range(n,0,-1):
#     if i == n:
#         print(i * ' ' + '*' + i* ' ')
#     elif i==1:
#         print(i* ' '+ '*' + (n-1)*'  '+ i *'*')
#     else:
#         print(i*' ' + '*' +( 2*(n-i)-1)*' ' + '*' +i*'')
# for i in range(n + 1):
#     if i == n:
#         print(i * ' ' + '*' + i * ' ')
#     elif i == 1:
#         print(i * ' ' + '*' + (n - 1) * '  ' + i * '*')
#     else:
#         print(i * ' ' + '*' + (2 * (n - i) - 1) * ' ' + '*' + i * ' ')
# for i in range(n+1):
#     print(i*' ' +( 2*(n-i)+1)*'*'+i*'')


n = int(input("number:"))
for i in range(n):
    print(" " * (n - i) + "*" * (i * 2 + 1))
for i in range(n, -1, -1):
    print(" " * (n - i) + "*" * (i * 2 + 1))

n = int(input("number:"))
for i in range(1, n + 1):
    print((n - i) * " " + i * " *")
for i in range(n - 1, 0, -1):
    print((n - i) * " " + i * " *")


