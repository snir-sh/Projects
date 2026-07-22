class Solution:
    def longestPalindrome(self, s: str) -> str:
        palindrom = []
        i = 0
        j = len(s) - 1
        
        for c1 in s:
            for c2 in reversed(s):
                if c1 == c2:
                    palindrom.append(c1)
                else:
                    if len(palindrom) > 1:
                        print(palindrom)
                    palindrom = []
                if i == j:
                    break
                j -= 1
            i += 1

s = Solution()
res = s.longestPalindrome("abacbcbc")
print(res)
