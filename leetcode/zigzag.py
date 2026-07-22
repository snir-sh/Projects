class Solution:
    def convert(self, s: str, numRows: int) -> str:
        print(len(s))
        if numRows == 1:
            return s

        lines = [""] * numRows
        index = 0
        direction = 1

        for c in s:
            lines[index] += c
            if direction == 1 and index == numRows - 1:
                direction = -1
            elif direction == -1 and index == 0:
                direction = 1
                
            index += direction

        return "".join(lines)
    

solution = Solution()
res = solution.convert("PAYPALISHIRING",1)
print(res)
