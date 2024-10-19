#memoisation

def memo(f):
    m = {}
    def checker(x):
        if x not in m:
            m[x]=f(x)
        return m[x]
    return checker

@memo
def fib(n):
    if n==0:
        return 0
    elif n==1:
        return 1
    else:
        return fib(n-1) + fib(n-2)
print(fib(8))



# nums = [2,2,1,1,1,2,2]
nums = [3,2,3]
d = {}
for i in nums:
    d[i]=d.get(i,0)+1
print(d)
for char in d.items():
    if max(d.values())==char[1]:
        print(char[0])

# res = ""
# inp = 's3t1z5'
# for i in range(0, len(inp), 2):
#     print(i,inp[i],int(inp[i + 1]))
#     for j in range(int(inp[i + 1])):
#         res = res + inp[i]
# print(res)

# filter_func = list(filter(lambda x: x%3==0, [1, 2, 3, 4, 5, 6, 7, 8, 9]))
# print(filter_func)

# weekdays = ['sun','mon','tue','wed','thu','fri','sat']
# listAsTuple = tuple(weekdays)
# print(listAsTuple)
# listList = list(weekdays)
# print(listList)

# l = [1,2,3]
# print(l[-1],l[-3])
# print(sum(range(1,100)))

# glover = 1
# def my_global():
#     global glover
#     glover = 2
# my_global()
# def my_local():
#     print(glover)
# my_local()


# n = 153
# a = list(map(int, (str(n))))
# print(a)
# s = list(map(lambda i: i ** 3, a))
# print(sum(s))

# fib  = [0,1]
# for i in range(5):
#     fib.append(fib[-1]+fib[-2])
# print(' '.join(str(e) for e in fib))
#
# d = {'a': 1,'b': 2}
# print(','.join(d))
# st = 'python'
# print(st.isalnum())
# st1 = '1'
# print(type(st1))
