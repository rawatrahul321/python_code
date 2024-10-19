my_list = [2, 3, 5, 7, 11]
squared_list = [x**2 for x in my_list]    # list comprehension
# output => [4 , 9 , 25 , 49 , 121]
squared_dict = {x:x**2 for x in my_list}    # dict comprehension
print([i for i in squared_dict.values()])
# result = 2
# count = 0
# while result!=512:
#     result = result*2
#     count+=1
# print(count)

arr  = ["rahul","ra","rah"]
d = arr.sort(key=lambda x:len(x),reverse=True)
print(arr)

# Reverse a string 
strin = "rahul"
string = list(strin)
print(string)
l,r = 0,len(string)-1
while l<r:
    string[l],string[r]=string[r],string[l]
    l+=1
    r-=1
print(string)

for i in string:
    stack.append(i)
i =0 
while stack:
    string[i]=stack.pop()
    i+=1
print(string)

strin = "rahul"
string = list(strin)
stack = [ ]
l =0
r = len(string)-1
def reverse(l,r):
    if l<r:
        string[l],string[r]=string[r],string[l]
    return string
print(reverse(l,r))