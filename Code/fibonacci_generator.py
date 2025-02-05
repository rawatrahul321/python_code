# num =10
# for n in range(2,num+1):
#     for i in range(2,n):
#         if n%i==0:
#             break
#     else:
#         print(n,end=" ")

# li = [(22,2,3,4,11,1),(22,222,3,4,11,1),(22,2,3,4,11,1)]
# one = [i[1] for i in li]
# print(one,end=" ")
def fib_gen(n):
    a,b= 0,1
    count = 0
    while count<n:
        yield a
        a,b=b,a+b
        count+=1
for i in fib_gen(100):
    print(i,end=" ")