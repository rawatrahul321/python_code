arr  = [1,2,3,3,3,3,4,5,4,5]
count = 0
num = arr[0]
for i in arr:
    feq = arr.count(i)
    if feq>count:
        count = feq
        num = i
print(num)

# def most_frequent(List):
#     counter = 0
#     num = List[0]
#     for i in List:
#         curr_frequency = List.count(i)
#         if (curr_frequency > counter):
#             counter = curr_frequency
#             num = i
#     return num
# List = [2, 1, 2, 2, 1, 3]
#
# print(most_frequent(List))

def twosum(nums,target):
    visited = set()
    tuples = []
    for num in nums:
        if target-num in visited:
            tuples.append([target-num,num])
        else:
            visited.add(num)
    return tuples

print(twosum([2,5,4,8,1],6))

def sort_aplha(string):
    li = sorted(list(string))
    new_letter = ''
    for i in li:
        new_letter+=i
    return new_letter
print(sort_aplha("hello"))

from collections import defaultdict

arr  = [1,2,3,3,3,3,4,5,4,5]
# count = 0
# # d = {}
# d = defaultdict(int)
# for i in arr:
#     d[i]+=1
# print(d)
# x  = max(arr,key=arr.count)
# print(x)