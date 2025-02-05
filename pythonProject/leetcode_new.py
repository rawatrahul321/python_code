def length_of_longest_substring(s):
    char_set = set()
    left, max_length = 0, 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_length = max(max_length, right - left + 1)
    return max_length,s

# Example
print(length_of_longest_substring("abcabcbb"))  # Output: 3



# nums = [4,1,2,1,2]
# def single_number(nums):
#     d = {}
#     for i in nums:
#         if i not in d:
#             d[i]=1
#         else:
#             d[i]+=1
#     for i in nums:
#         if d[i]==1:
#             return i
# print(single_number(nums))


# string1 = 'loveleetcode'
# def first_single_char(string1):
#     d = list(string1)
#     dq = {}
#     for i in string1:
#         if i not in dq:
#             dq[i]=True
#         else:
#             dq[i]=False
#     for i,c in enumerate(string1):
#         if dq[c]:
#             return i
# print(first_single_char(string1))

# Revserse String

# arr = ['h','e','l','l','o']
# left,right=0,len(arr)-1
# while left<right:
#     arr[left],arr[right]=arr[right],arr[left]
#     left+=1
#     right-=1
# print(arr)

# nums = [0,1,0,3,12]
# def last_zero(nums):
#     prev = 0
#     for i in range(len(nums)):
#         if nums[i]!=0:
#             nums[prev],nums[i]=nums[i],nums[prev]
#             prev+=1
#     return nums
# print(last_zero(nums))

def longest_common_string(strs):
    prefix  = ''
    for z in zip(*strs):
        if len(set(z))==1:
            prefix += z[0]
        else:
            break
    return prefix
print(longest_common_string(["flower", "flow", "flight"]))

def highest_product(list_of_ints):
    if len(list_of_ints) < 3:
        return None
    sorted_ints = sorted(list_of_ints)
    print (sorted_ints[0] , sorted_ints[1] , sorted_ints[-1], sorted_ints[-3] , sorted_ints[-2] , sorted_ints[-1])
    return max(sorted_ints[0] * sorted_ints[1] * sorted_ints[-1], sorted_ints[-3] * sorted_ints[-2] * sorted_ints[-1])
    # return sorted_ints[-1]*sorted_ints[-2]*sorted_ints[-3]
print(highest_product([-100,-98,-1,2,3,4]))
