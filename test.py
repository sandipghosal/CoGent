a = [1, 1, 2, 1, 3, 1, 3, 2, 2, 4, 4, 5, 4, 6, 4, 6, 7]
b = a.copy()
c = a.copy()

print(a)
for i in b:
    for j in c:
        print('b: ', b)
        print('c: ', c)
        print('i= ', i)
        print('j= ', j)
        if id(i)!=id(j) and i == j:
            a.remove(j)
            print('a: ', a)

print(a)
