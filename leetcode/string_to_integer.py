class Solution:
    def myAtoi(self, s: str) -> int:
        number = ''
        sign = ''
        if not s:
            return 0
        for c in s:
            if c in ['+', '-'] and not number and not sign:
                sign = c
            elif c.isdigit():
                number += c
            elif c == ' ' and not number and not sign:
                continue
            else:
                break
        number = int(number) * (-1 if sign == '-' else 1) if number else 0
        if number < -2**31:
            return -2**31
        elif number > 2**31 - 1:
            return 2**31 - 1
        return number
            
res = Solution().myAtoi("  +  413")
print(res)

        
        