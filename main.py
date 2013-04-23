import timeit
setup = '''
import pygame
import random


d = pygame.Rect(0,0,10,10)
b = pygame.Rect(12, 12, 10, 10)
c = pygame.Rect(5, 5, 10, 10)
print c
print d
print b

s = [random.random() for i in range(100)]

timsort = list.sort
'''






print min(timeit.Timer('a=s[:]; timsort(a)', setup=setup).repeat(7, 100))
