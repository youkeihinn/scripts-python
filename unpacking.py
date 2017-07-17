#a, *b, c = [2, 7, 5, 6, 3, 4, 1]
#print(a)
#print(b)
#print(c)

def repeat(count,name):
    for i in range(count):
        print(name)

print('Call function repeat using a list of arguments:')
args = [2,"cats"]
repeat(*args)

print("Call function repeat using a dictionary of keyword arguments:")
args2 = {'count':4,'name':'cats'}
repeat(**args2)
