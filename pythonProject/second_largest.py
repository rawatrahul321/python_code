my_nums = [0,15,68,1,0,-55]
def get_largest(nums):
    largest = nums[0]
    for num in nums:
        if num>largest:
            largest = num
    return largest
print(get_largest(my_nums))
my_nums = [0,15,68,1,0,-55]

def get_second_largest(nums):
    largest = nums[0]
    second_largest = nums[0]
    for i in range(1,len(nums)):
        if nums[i]>largest:
            second_largest = largest
            largest = nums[i]
        elif nums[i]>second_largest:
            second_largest = nums[i]
    return second_largest
print(get_second_largest(my_nums))