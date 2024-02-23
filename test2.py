from copy import deepcopy

list1 = []
list2 = deepcopy(list1).append(5)
print(list2)