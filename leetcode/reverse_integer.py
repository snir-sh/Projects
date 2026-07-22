class Solution:
    def reverse(self, x: int) -> int:
        sign = -1 if x < 0 else 1
        x = abs(x)
        _, rev_num = self.recursive_reverse(x, 0)
        rev_num = rev_num * sign
        return rev_num if rev_num >= -2**31 and rev_num <= 2**31 - 1 else 0
    

    def recursive_reverse(self, num, rev_num):
        if num > 0:
            rev_num = rev_num * 10 + num % 10
            num = num // 10
            return self.recursive_reverse(num, rev_num)
        return num, rev_num
    
    
solution = Solution()
res = solution.reverse(1534236469)
print(res)
