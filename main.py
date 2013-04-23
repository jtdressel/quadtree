import timeit

setup = '''
import random

random.seed('slartibartfast')
s = [random.random() for i in range(100)]
timsort = list.sort

'''

print min(timeit.Timer('a=s[:]; timsort(a)', setup=setup).repeat(7, 100))
