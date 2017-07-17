from itertools import permutations,combinations,chain

for p in permutations([1,2,3]):
    print(p)

print('++++++++++++++++')
for c in combinations([1,2,3,4],2):
    print(c)

print('++++++++++++++++')
for i in chain(range(3),range(12,15)):
    print(i)
