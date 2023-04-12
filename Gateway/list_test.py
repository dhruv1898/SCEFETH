asp = ['a', False, 'f', 'h', False, False, 'e']

p = 0

for i in range(0, len(asp)):
    print(asp[p])
    if not asp[p]:
        print("got fasle")
        p+=1
    else:
        print(asp[p])
        asp.pop(p)

print(asp)

f = []

if len(asp) > 0:
    print("len is more")