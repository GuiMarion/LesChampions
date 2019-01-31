import numpy as np


def kikou(seed):
	np.random.seed(seed)
	return getTamere(10)

def getTamere(n):
	return np.random.normal(10, 2, n)
