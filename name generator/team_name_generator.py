import numpy as np
lines = open('british-english').read().splitlines()
a=lines[np.random.randint(0,99000)]
b=lines[np.random.randint(0,99000)]
print(a+' ' +b)