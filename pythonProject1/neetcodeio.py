s = 'leet**cod*e'
def remove_star_left(s):
    stack = []
    for i in s:
        if i=='*':
            stack and s.pop()
        else:
            stack.append(i)
    return stack
print(remove_star_left(s))

# Sort based on Frequency 
nums  = [1,1,2,2,2,3]
from collections import Counter
print(Counter(nums))
f = Counter(nums)
nums.sort(key=lambda x:(-f[x],x),reverse=True) 
print(nums)

l = []
d = {}
for i in nums:
    d[i]=d.get(i,0)+1
    f = sorted(nums,key=nums.count,reverse=False)
print(d,f)