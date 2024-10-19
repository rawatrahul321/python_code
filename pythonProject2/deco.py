# string='aaaabbbcc'
# #output=4a3b2c
# d = []
# s = []
# sn = list(string)
# for i in sn:
#     if i not in d:
#         d.append(str(sn.count(i))+i)
# for d1 in d:
#     if d1 not in s:
#         s.append(d1)
# print("".join(s))  

# string='a4b3c2'
# x=''
# for i in string:
#     if i.isalpha():
#         f=i
#     else:
#         x=x+f*int(i)
   
# print(x)

str1 = '4a2b3c1d'
out  = ""
for i in str1:
    if not i.isalpha():
        x = i
    else:
        out = out+int(x)*i
print(out)

# string="mynameisrahul"
# i=0
# print("even number strings are follows")

# while(i<len(string)):
#     if i%2==0:
#         print(string[i])
#     i=i+2
# i=0

# string='my name is rahul and I am python Developer'
# s=string.split()
# n=[]
# i=0
# while i<len(s):
#     if i%2==0:
#         n.append(s[i])
#     else:
#         n.append(s[i][::-1])
#     i=i+1
   
# print(n)

# x= range(5)
# def add():
#     for i in x:
#         yield i*i       
# a=add()
# for i in a:
#     print(i)

# def decorator_message(fun):
#     def add(addd):
#         return addd+12       
#     return add
# def decorator_sub(fun):
#     def sub(subb):
#         return subb-11
#     return sub
   
# @decorator_message
# def adddd(addd):
#     return addd
   
# @decorator_sub
# def subbbb(subb):
#     return subb
# print(adddd(23))
# print(subbbb(45))