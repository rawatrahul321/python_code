def thirdMax(nums):
    max_set = set()
    for num in nums:
        max_set.add(num)
        if len(max_set) > 3:
            max_set.remove(min(max_set))
    if len(max_set) < 3:
        return max(max_set)
    else:
        return min(max_set)
nums1 = [3, 2, 1]
print(thirdMax(nums1))  # Output: 1
nums2 = [1, 2]
print(thirdMax(nums2))  # Output: 2
nums3 = [2, 2, 3, 1]
print(thirdMax(nums3))  # Output: 1

def thirdMax(nums):
    # Remove duplicates and sort in descending order
    unique_nums = sorted(set(nums), reverse=True)
    
    # Check if there are at least three unique numbers
    if len(unique_nums) >= 3:
        return unique_nums[2]  # Return the third distinct maximum
    else:
        return max(unique_nums)  # Return the maximum number

# Example usage:
nums1 = [3, 2, 1]
print(thirdMax(nums1))  # Output: 1

nums2 = [1, 2]
print(thirdMax(nums2))  # Output: 2

nums3 = [2, 2, 3, 1]
print(thirdMax(nums3))  # Output: 1

