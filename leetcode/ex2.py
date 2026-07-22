
nums1 = [1,2,3,4,5]

nums2 = [6,7,8,9,10,11,12,13,14,15,16,17]
new_list = []

i, j = 0, 0

while i < len(nums1) or j < len(nums2):
    left = nums1[i] if i < len(nums1) else 10**6 + 1  
    right = nums2[j] if j < len(nums2) else 10**6 + 1 
    if left <= right:
        new_list.append(int(left))
        i += 1
    else:
        new_list.append(int(right))
        j += 1 

length = len(new_list)
if length % 2 != 0:
    print(new_list[length // 2])
else:
    print((new_list[(length // 2) -1] + new_list[length // 2])/2)


