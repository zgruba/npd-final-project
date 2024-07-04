import numpy as np

def hello(name, size):
    zeros = np.zeros(size)
    print(f"Hello {name}! We can use numpy.zeros({size}): {zeros}")