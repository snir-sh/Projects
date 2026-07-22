class Solution:
    def isPalindrome2(self, x: int) -> bool:
        if x < 0:
            return False
        str_x = str(x)
        return str_x == str_x[::-1]

    def isPalindrome(self, x: int) -> bool:
        if x < 0:
            return False
        index = 0
        back_index = len(str(x)) - 1
        str_x = str(x)
        while index < back_index:
            if str_x[index] == str_x[back_index]:
                index += 1
                back_index -= 1
                continue
            return False
        return True
        
    
s = Solution()
print(s.isPalindrome(121))
print(s.isPalindrome(-121))
print(s.isPalindrome(10))
