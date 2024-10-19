def splitArray(nums, k):
    def countGroups(maxSum):
        groups = 1
        currentSum = 0
        for num in nums:
            currentSum += num
            if currentSum > maxSum:
                groups += 1
                currentSum = num
        print(currentSum,groups,"LLLLL")
        return groups

    left = max(nums)
    right = sum(nums)
    while left < right:
        mid = left + (right - left) // 2
        if countGroups(mid) > k:
            left = mid + 1
        else:
            right = mid
        print(left,right,mid,"llllllldldld")

    return left

# Test cases
nums1 = [7, 2, 5, 10, 8]
k1 = 2
print(splitArray(nums1, k1))  # Output: 18

# nums2 = [1, 2, 3, 4, 5]
# k2 = 2
# print(splitArray(nums2, k2))  # Output: 9
