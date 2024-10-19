list1 = [4,3,2,5,1]
n = len(list1)
for i in range(0,n):
    for j in range(i+1,n):
        print(list1,"list2")
        if list1[i]>list1[j]:
            list1[i],list1[j]=list1[j],list1[i]
print(list1)

# my_nums = [222,322,4,22,212,6]

# def get_second_smallest(nums):
#     smallest = float('inf')
#     second_smallest = float('inf')
#     for i in range(len(nums)):
#         if my_nums[i]<smallest:
#             second_smallest = smallest
#             smallest = my_nums[i]
#         elif my_nums[i]<second_smallest:
#             second_smallest = my_nums[i]
#     return second_smallest

# print(get_second_smallest(my_nums))

