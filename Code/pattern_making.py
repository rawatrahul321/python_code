from functools import reduce
def factorial(n):
    return reduce(lambda x,y:x*y,range(1,n+1))
   
print(factorial(6))

# colors = ['orange','Red','GdGGGreen','black']
# normalized = sorted(colors,key=lambda s:s.casefold())
# print(normalized)
# s = 'rahul  '
# print(s.casefold())

# n=int(input("enter the number:"))
# for i in range(n-1):
#    print((n-i) * " "+(n*2+i) * " * ")

# for i in range(n-1,-1,-1):
   
#    print((n-i) * " "+(n*2+i) * " * ")

# n=int(input("enter the number:"))
# for i in range(n-1):
#     print(" "*(n-i), "*"*(i    *2+1))

# for i in range(n):
#     print(i*"  "+(n-i)*" "+(n-i)*"*")