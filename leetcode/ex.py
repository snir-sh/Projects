# class Solution:
#     def twoSum(self, nums: List[int], target: int) -> List[int]:
#         for i, x in enumerate(nums):
#             for j in range(i+1, len(nums)):
#                 if x + nums[j] == target:
#                     return [i, j]


# s = Solution()
# res = s.twoSum([1,2,3,4], 5)
# print(res)

# a = 10
# b = 22
# print(b//10)
# print(int(b/10))

def lengthOfLongestSubstring(s: str) -> int:
    subset = ""
    max_size = 0
    for letter in s:
        if letter not in subset:
            subset += letter
        else:
            max_size = max(max_size, len(subset))
            subset = subset[subset.index(letter)+1:] + letter

    return max(max_size, len(subset))

print(lengthOfLongestSubstring("abacbcbc"))
