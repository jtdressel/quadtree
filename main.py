import timeit
setup = '''

import pygame
import random
from quadtree import *

d = pygame.Rect(0,0,10,10)
b = pygame.Rect(12, 12, 10, 10)
c = pygame.Rect(5, 5, 10, 10)
print c
print d
print b
id2rect = {1: d, 2: b, 3: c}

quadtree = QuadTree(id2rect, pygame.Rect(0,0,100,100))


'''






print min(timeit.Timer('pass', setup=setup).repeat(7, 100))
