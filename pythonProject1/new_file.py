a = 'abcduuubc'
char_index = {}
res = -1
for i, j in enumerate(a):
    if j in char_index:
        res = max(res, i - char_index[j] - 1)
    else:
        char_index[j] = i
print(res)



# n = int(input("Enter the numer:"))
# k = 1
# for i in range(5):

#     for j in range(i):
#         print(k,end=" ")
#         k+=1
#     print()



# def multiple(func):
#     def inner(a,b):
#         print("I want to Mulitple")
#         return func(a,b)
#     return inner
#
# @multiple
# def m(a,b):
#     return a*b
# print(m(3,4))

# def add(func):
#     def inner():
#         print("hello")
#         func()
#     return inner

# @add
# def hello():
#     print("Rahul")

# @add 
# def deepak():
#     print("Deepak")

# hello()
# deepak()

# class Person:
#     def walk(self,name):
#         self.name = name
#         return name
#     def __init__(self):
#         print("Rawat")

# p = Person()
# print(p.walk("Rahul"))
