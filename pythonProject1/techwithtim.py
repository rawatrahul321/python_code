arr = [1,2,3,4]
for i in arr:
    print(i,sep=".\n",end=" ")

# li = {'a':1}
# li1 = {'b':2}
# li |= li1
# print(li)


# from collections import Counter
# arr = [1,2,3,4,1,2,3]
# c = Counter(arr)
# print(c.most_common())

# def get_func():
#     users: dict[int,str] = {1:"r",2:"e"}
#     return users
# print(get_func())

# Closure 
# def adder(n):
#     def inner_adder(a):
#         return n+a
#     return inner_adder
# d = adder(5)
# d1  = d(4)
# print(d1)

# def functional_caller(func,*args,**kwargs):
#     return func(*args,**kwargs)

# def add(a,b):
#     return a+b
# print(functional_caller(add,1,2))


# strings = ['rahul','vin','dee']
# mapped = list(map(len,strings))
# mapped = list(map(lambda x:x+'s',strings))
# print(mapped)


# r  = range(10)
# print(r) 
# a,b,*c = [1,2,3,4]
# print(f"{a}")
# li = [1,2,3]
# li1 = [4,5,6]
# print(*li,*li1)
# def demo_eval():
#     n = input("Enter the Expression:")
#     s = eval(n)
#     print(f"{s}")
# demo_eval()

# name:int = [1,2,3]
# li = str(name)
# print(li,type(li))

# with open("file.txt","w") as f:
#     f.write("LLL")
# with open("file.txt",'r') as f:
#     content = f.read()
#     print(f"{content}")