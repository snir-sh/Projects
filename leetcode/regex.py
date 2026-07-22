# class Solution:
#     def isMatch(self, s: str, p: str) -> bool:
#         pattern_index = 0
#         string_index = 0
#         last_letter = ''
#         while pattern_index < len(p) and string_index < len(s):
#             if s[string_index] == p[pattern_index] or p[pattern_index] == '.':
#                 last_letter = s[string_index]
#                 if pattern_index + 1 < len(p) and p[pattern_index+1] == '*':
#                     string_index += 1
#                 else:
#                     string_index += 1
#                     pattern_index += 1
#             elif p[pattern_index] == '*':
#                 string_index +=1
#             else:
#                 if pattern_index + 1 < len(p) and p[pattern_index+1] == '*':
#                     string_index += 1
#                     pattern_index += 2
#                 else:
#                     return False
#         if string_index < len(s):
#             return False
#         return True
    
# class Solution:
#     def isMatch(self, s: str, p: str) -> bool:
#         pattern_index = 0
#         string_index = 0
#         last_letter = ''

#         while pattern_index < len(p) and string_index < len(s):
#             current_pattern = p[pattern_index]
#             current_char = s[string_index]

#             next_is_star = (
#                 pattern_index + 1 < len(p)
#                 and p[pattern_index + 1] == '*'
#             )

#             current_matches = (
#                 current_pattern == '.'
#                 or current_pattern == current_char
#             )

#             if current_matches:
#                 string_index += 1

#                 if next_is_star:
#                     last_letter = current_char
#                 else:
#                     pattern_index += 1
#                     last_letter = ''

#             elif current_pattern == '*' and last_letter == current_char:
#                 string_index += 1

#             elif next_is_star:
#                 pattern_index += 2

#             else:
#                 return False

        # return string_index == len(s)




# class Solution:
#     def isMatch(self, s: str, p: str) -> bool:
#         pattern_index = 0
#         string_index = 0
#         last_letter = ''
#         while pattern_index < len(p) and string_index < len(s):
#             if p[pattern_index] == '.' or (p[pattern_index] == '*' and last_letter == ''):
#                 string_index += 1
#                 pattern_index += 1
#             elif s[string_index] == p[pattern_index]:
#                 if pattern_index + 1 < len(p) and p[pattern_index+1] == '*':
#                     last_letter = s[string_index]
#                     string_index += 1
#                     pattern_index += 1
#                 else:
#                     pattern_index += 1
#                     string_index += 1
#                     last_letter = ''
#             elif p[pattern_index] == '*' and last_letter == s[string_index]:
#                 string_index += 1
#             elif pattern_index + 1 < len(p) and p[pattern_index] == '*':
#                 pattern_index += 1
#             else:
#                 return False
                
#         if string_index < len(s):
#             return False
#         return True



solution = Solution()
# print(solution.isMatch("aa", "a"))
# print(solution.isMatch("aa", "a*"))
print(solution.isMatch("ab", ".*"))
print(solution.isMatch("aab", "c*a*b"))
# print(solution.isMatch("mississippi", "mis*is*p*."))
# print(solution.isMatch("mississippi", "mis*is*ip*."))
