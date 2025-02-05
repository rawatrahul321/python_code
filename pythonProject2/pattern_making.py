def longest_increasing_sequence(nums):
    n = len(nums)
    dp = [1]*n
    for i in range(n):
        for j in range(i):
            if nums[i]>nums[j]:
                dp[i]=max(dp[i],dp[j]+1)
    return max(dp)
nums = [10, 9, 2, 5, 3, 7, 101, 18]
print(longest_increasing_sequence(nums))


# Kadane's Algorithm

def max_subarray(nums):
    max_current = max_global = nums[0]
    for i in range(1,len(nums)):
        max_current = max(nums[i],max_current + nums[i])
        max_global = max(max_current,max_global)
    return max_global

nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
print(max_subarray(nums))


# from functools import reduce
# def factorial(n):
#     return reduce(lambda x,y:x*y,range(1,n+1))
   
# print(factorial(6))

# colors = ['orange','Red','GdGGGreen','black']
# normalized = sorted(colors,key=lambda s:s.casefold())
# print(normalized)
# s = 'rahul  '
# print(s.casefold())

# n=int(input("enter the number:"))
# for i in range(n-1):
#    print((n-i) * " "+(n*2+i) * " * ")

# for i in range(n-1,-1,-1):
   
#    print((n-i) * " "+(n*2+i) * " * ")

# n=int(input("enter the number:"))
# for i in range(n-1):
#     print(" "*(n-i), "*"*(i    *2+1))

# for i in range(n):
#     print(i*"  "+(n-i)*" "+(n-i)*"*")