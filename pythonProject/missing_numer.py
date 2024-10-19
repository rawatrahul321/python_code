class Solution(object):
   def missingNumber(self, nums):
      nums.sort()
      high = len(nums)
      low = 0
      print(nums,len(nums))
      while low<high:
         mid = low + (high-low)//2
         if nums[mid]>mid:
            high = mid
            print(high,mid,nums[mid],"hifgh")
         else:
            low = mid+1
            print(low,mid,"low")
      return low
ob1 = Solution()
print(ob1.missingNumber([5,3,1,7,8,0,9,2,4]))