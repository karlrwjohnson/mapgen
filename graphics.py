import pygame
import sys

from debug import *

MAIN = sys.modules['__main__']

@debug
def screenCoord(point):
  return int(point[0] * MAIN.SIZE[0]), int(point[1] * MAIN.SIZE[1])

def drawSegment(segment, color):
  pygame.draw.line(MAIN.SURF, color, screenCoord(segment[0]), screenCoord(segment[1]), 2)

def waitForKey():
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT or \
         (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
        sys.exit()
      elif event.type == pygame.KEYDOWN:
        return
    pygame.time.wait(100)

def waitForDelay():
  pygame.time.wait(MAIN.ARGS.delay);
  for event in pygame.event.get():
    if event.type == pygame.QUIT or \
       (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
      sys.exit()

