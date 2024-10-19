numbers=[3,2,31,3,3,2]
def square(number):
    return number*number
l=list(map(square,numbers))
print(l)
def odd(number):
    return bool(number%2!=0)
   
print(list(filter(lambda i:i%2==0,l)))

# string=[1,2,3,4,5,1,21,2]
# d={}
# for i in string:
#     d[i]=d.get(i,0)+1
# print(d) 
# for k,v in d.items():
#     print("{} occurs {} times".format(k,v))

# li = [1,2,3,4,6]
# l = li.pop()
# print(l,li)
# t = (1,2,3,22,2,3,44)
# print(t,type(t))
# t1 = sorted(t)
# print(t1,type(t1))
# def thirdMax(nums):
#     max_set = set()
#     for num in nums:
#         max_set.add(num)
#         if len(max_set) > 3:
#             max_set.remove(min(max_set))
#     if len(max_set) < 3:
#         return max(max_set)
#     else:
#         return min(max_set)
# nums1 = [3, 2, 1]
# print(thirdMax(nums1))  # Output: 1
# nums2 = [1, 2]
# print(thirdMax(nums2))  # Output: 2
# nums3 = [2, 2, 3, 11,2,3,4]
# print(thirdMax(nums3))  # Output: 1

def thirdMax(nums):
    unique_nums = sorted(set(nums), reverse=True)
    print(unique_nums)
    if len(unique_nums) >= 3:
        return unique_nums[2]  # Return the third distinct maximum
    else:
        return max(unique_nums)  # Return the maximum number
nums1 = [1,2,3]
print(thirdMax(nums1))  # Output: 1

# nums2 = [1, 2]
# print(thirdMax(nums2))  # Output: 2

# nums3 = [2, 2, 3, 1]
# print(thirdMax(nums3))  # Output: 1

