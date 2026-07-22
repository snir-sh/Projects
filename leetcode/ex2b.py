class Solution:
    def findMedianSortedArrays(self, nums1, nums2):

        # Binary search on smaller array
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        m, n = len(nums1), len(nums2)

        total = m + n
        half = (total + 1) // 2

        left = 0
        right = m

        while left <= right:

            partition1 = (left + right) // 2
            partition2 = half - partition1

            left1 = float("-inf") if partition1 == 0 else nums1[partition1 - 1]
            right1 = float("inf") if partition1 == m else nums1[partition1]

            left2 = float("-inf") if partition2 == 0 else nums2[partition2 - 1]
            right2 = float("inf") if partition2 == n else nums2[partition2]

            # Correct partition
            if left1 <= right2 and left2 <= right1:

                # Odd total length
                if total % 2:
                    return max(left1, left2)

                # Even total length
                return (
                    max(left1, left2) +
                    min(right1, right2)
                ) / 2

            # Move left
            elif left1 > right2:
                right = partition1 - 1

            # Move right
            else:
                left = partition1 + 1
                

s = Solution()

res = s.findMedianSortedArrays([1,2,3,4], [5,6,7,8])

print(res)
