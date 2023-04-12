from copy import deepcopy

Enddevices = ['ID001','ID003','ID004']

d = {}
l = []
for x in Enddevices:
    d[x]=[]

print(d)

d['ID001'].append('Data to 1')

print(d)

f = deepcopy(d)

f['ID002'], f['ID005']='data modified', 'data2'

print(type(d))
print(type(f))

l.append(f)

s = l[0]

print(s)

print(type(s))

g = ['ID001','ID003','ID004']

if type(g)!= type(None):
    print("a")

l = {'a':'b', 'c':'d'}

print(l)

l['e'] = 'f'

print(l)