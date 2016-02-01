#!/usr/bin/env python

import argparse
import itertools
import json
import random
import sys

from debug import *
from geometry import *

PARSER = argparse.ArgumentParser(description='Voroni Diagram Generator')
PARSER.add_argument('--num_points', default=20, type=int, help='Number of random points to generate')
PARSER.add_argument('--animate', action='store_true', help='Animate the segment consideration algorithm')
PARSER.add_argument('--interactive', action='store_true', help='Pause after every segment consideration (requires --interactive)')
PARSER.add_argument('--delay', default=50, type=int, help='Time to show each frame, in milliseconds (requires --animate)')
PARSER.add_argument('--profile', action='store_true', help='Count the number of times certain functions are called')
saveLoadPoints = PARSER.add_mutually_exclusive_group()
saveLoadPoints.add_argument('--save_points', help='Save randomly-generated points out to a file')
saveLoadPoints.add_argument('--load_points', help='Load previously-generated points from a file')
ARGS = PARSER.parse_args()

SIZE = 800, 800
RED = 255,0,0
PINK = 255,200,200
LAVENDER = 200,200,255
GOLD = 200,200,0
GREEN = 0,200,0
BLUE = 0,0,255
DARK_BLUE = 0, 0, 127
BLACK = 0,0,0
WHITE = 255,255,255
GRAY = 180,180,180
POINT_COLOR = BLUE
ACTIVE_POINT_COLOR = GREEN
OTHER_POINT_COLOR = GOLD
LINE_COLOR = DARK_BLUE
ACTIVE_LINE_COLOR = GREEN
POINT_RADIUS = 5
LINE_WIDTH = 1

if ARGS.profile:
  enable_profiling()

if ARGS.animate:
  import pygame

  pygame.init()
  SCREEN = pygame.display.set_mode(SIZE)
  SURF = pygame.display.get_surface()

  from graphics import *

# Points generation

if ARGS.load_points:
    with open(ARGS.load_points) as infile:
        points = json.load(infile)
else:
    points = [
      (random.random(), random.random())
      for i in range(ARGS.num_points)
    ]

if ARGS.save_points:
    with open(ARGS.save_points, 'w') as outfile:
        json.dump(points, outfile)

# Globals for segment consideration
shapes = []
activeShape = None
consideringPoint = None



class Shape (object):
  def __init__(self, core):
    self.core = core
    self.vertices = [(0,0), (1,0), (1,1), (0,1)]


def drawPoly(poly, color):
  for index in range(len(poly)):
    drawSegment((poly[index-1], poly[index]), color)

def render ():
  SCREEN.fill(WHITE);
  for shape in shapes:
    drawPoly(shape.vertices, LINE_COLOR)
  if activeShape is not None:
    drawPoly(activeShape.vertices, ACTIVE_LINE_COLOR)
  for point in points:
    pygame.draw.circle(SURF, POINT_COLOR, screenCoord(point), POINT_RADIUS)
  if activeShape is not None:
    pygame.draw.circle(SURF, ACTIVE_POINT_COLOR, screenCoord(activeShape.core), POINT_RADIUS)
  if consideringPoint is not None:
    pygame.draw.circle(SURF, OTHER_POINT_COLOR, screenCoord(consideringPoint), POINT_RADIUS)

  pygame.display.flip();

if ARGS.animate:
  render()
  if ARGS.interactive:
    waitForKey()
  else:
    waitForDelay()

for p in points:
  s = Shape(p)
  activeShape = s
  for q in points:
    consideringPoint = q
    if p != q:
      # Midpoint and slope of perpendicular bisector
      position = tuple((p + q) / 2.0 for (p, q) in zip(p, q))
      (dx, dy) = vecSubtract(q, p)
      slope    = (dy, -dx) # 90-degree counterclockwise rotation

      s.vertices = cutShape(s.core, s.vertices, position, slope)

      if ARGS.animate:
        render()
        if ARGS.interactive:
          waitForKey()
        else:
          waitForDelay()

  shapes.append(s)

activeShape = None
consideringPoint = None

if ARGS.profile:
  for (func, count) in call_counts.items():
    print "{}.{}: {}".format(func.__module__, func.__name__, count)

if ARGS.animate:
  render()
  waitForKey()
