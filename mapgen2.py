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
PARSER.add_argument('--interactive', action='store_true', help='Pause after every segment consideration (requires --animate)')
PARSER.add_argument('--delay', default=50, type=int, help='Time to show each frame, in milliseconds (requires --animate)')
PARSER.add_argument('--display', action='store_true', help='Don\'t render every frame, just the last one')
PARSER.add_argument('--profile', action='store_true', help='Count the number of times certain functions are called')
PARSER.add_argument('--cell_optimization', type=int, help='Divide the field into n-by-n cells to decrease the number of comparisons')
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
CELL_LINE_COLOR = GRAY
POINT_RADIUS = 5
LINE_WIDTH = 1

if ARGS.profile:
  enable_profiling()

if ARGS.animate or ARGS.display:
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
  if ARGS.cell_optimization:
    for i in range(1, ARGS.cell_optimization):
      j = float(i) / ARGS.cell_optimization
      drawSegment(((0,j),(1,j)), CELL_LINE_COLOR)
      drawSegment(((j,0),(j,1)), CELL_LINE_COLOR)
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

def bucketPoints (points, divs):
  point_cells = {
    (x, y): []
    for x in range(0, divs)
    for y in range(0, divs)
  }

  for point in points:
    point_cells[(int(point[0] * divs), int(point[1] * divs))].append(point)

  return point_cells

def bucketIterator (buckets):
  for ((x, y), bucket) in buckets.items():
    adjacent_buckets = [bucket]
    if (x+1, y) in buckets: adjacent_buckets.append(buckets[(x+1, y)])
    if (x-1, y) in buckets: adjacent_buckets.append(buckets[(x-1, y)])
    if (x, y+1) in buckets: adjacent_buckets.append(buckets[(x, y+1)])
    if (x, y-1) in buckets: adjacent_buckets.append(buckets[(x, y-1)])
    if (x+1, y+1) in buckets: adjacent_buckets.append(buckets[(x+1, y+1)])
    if (x-1, y+1) in buckets: adjacent_buckets.append(buckets[(x-1, y+1)])
    if (x+1, y-1) in buckets: adjacent_buckets.append(buckets[(x+1, y-1)])
    if (x-1, y-1) in buckets: adjacent_buckets.append(buckets[(x-1, y-1)])
    for item in bucket:
      yield (item, itertools.chain.from_iterable(adjacent_buckets))

def nonOptimizedIterator (points):
  for p in points:
    yield (p, points)


for (p, other_points) in (
  bucketIterator(bucketPoints(points, ARGS.cell_optimization)) if ARGS.cell_optimization else
  nonOptimizedIterator(points)
):
  s = Shape(p)
  activeShape = s
  for q in other_points:
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

if ARGS.animate or ARGS.display:
  render()
  waitForKey()
