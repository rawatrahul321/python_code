def largest_number(nums):
    def compare(x, y):
        xy = int(x + y)
        yx = int(y + x)
        return xy - yx

    # Bubble sort
    n = len(nums)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if compare(str(nums[j]), str(nums[j + 1])) < 0:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]

    result = ''.join(map(str, nums))

    # Remove leading zeros
    result = result.lstrip('0')

    # Return "0" if the result is an empty string (all numbers were zero)
    return result if result else "0"

# Example 1
nums1 = [10, 2]
output1 = largest_number(nums1)
print(output1)  # Output: "210"

# Example 2
nums2 = [3, 30, 34, 5, 9]
output2 = largest_number(nums2)
print(output2)  # Output: "9534330"

# Nested Exapmples 

def pop(list):
    def remove_last(my_list):
        return my_list[len(list)-1]
    list.remove(remove_last(list))
    return list
list = [1,2,3,4,5]
print(pop(list))
print(pop(list))
print(pop(list))

# Closure
def outerfunc(x):
    def innerfunc(y):
        return pow(x,y)
    return innerfunc
a = outerfunc(2)
del outerfunc

print(a(3))
# dt = {5:4, 1:6, 6:3}
# sorted_dt = {key: value for key, value in sorted(dt.items(), key=lambda item: item[1])}
# print(sorted_dt)