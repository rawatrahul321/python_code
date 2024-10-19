def print_all(*args):
    for i in enumerate(args):
        print(i,list(i))
a=print_all(32,3,213,12,312,321,"dsadsad")
print(a)
print(type(a))


# D=dict.fromkeys(['a','b','c'],2)
# print(D)

# D={x.upper(): x*3 for x in 'abcd'}
# print(D)
# D={x:x**2 for x in [1,2,3,4]}
# print(D)
# print((D.keys()),end=",")
# print(list(D.values()))