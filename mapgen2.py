#!/usr/bin/env python

import argparse
import functools
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
PARSER.add_argument('--relaxation_passes', default=0, type=int)
PARSER.add_argument('--relaxation_factor', default=100.0, type=float)
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


shapes = []

class Shape (object):
  def __init__(self, core):
    self.core = core
    self.vertices = [(0,0), (1,0), (1,1), (0,1)]

def drawPoly(poly, color):
  for index in range(len(poly)):
    drawSegment((poly[index-1], poly[index]), color)

class ClearScreenRenderer (object):
  def __init__(self, color):
    self.color = color
  def render (self):
    SCREEN.fill(self.color)

class CellGridRenderer (object):
  def __init__(self, x_divs, y_divs, color):
    self.x_divs = x_divs
    self.y_divs = y_divs
    self.color = color
  def render(self):
    for i in range(1, self.x_divs):
      x = float(i) / self.x_divs
      drawSegment(((x,0),(x,1)), self.color)
    for i in range(1, self.y_divs):
      y = float(i) / self.y_divs
      drawSegment(((0,y),(1,y)), self.color)

class PointListRenderer (object):
  def __init__(self, point_list, color, radius=POINT_RADIUS):
    self.point_list = point_list
    self.color = color
    self.radius = radius
  def render(self):
    for point in self.point_list:
      pygame.draw.circle(SURF, self.color, screenCoord(point), self.radius)

class PointMovementRenderer (object):
  def __init__(self, point_list_list, color):
    self.point_list_list = point_list_list
    self.color = color
  def render(self):
    for listIdx in range(len(self.point_list_list)-1):
      for pointIdx in range(len(self.point_list_list[listIdx])):
        drawSegment(
          (
            self.point_list_list[listIdx][pointIdx],
            self.point_list_list[listIdx+1][pointIdx]
          ),
          self.color
        )

class PointRenderer (object):
  def __init__(self, point, color, radius=POINT_RADIUS):
    self.point = point
    self.color = color
    self.radius = radius
  def render(self):
    if self.point:
      pygame.draw.circle(SURF, self.color, screenCoord(self.point), self.radius)

class ShapeListRenderer (object):
  def __init__(self, shape_list, color):
    self.shape_list = shape_list
    self.color = color
  def render(self):
    for shape in self.shape_list:
      drawPoly(shape.vertices, self.color)

class ShapeRenderer (object):
  def __init__(self, shape, color):
    self.shape = shape
    self.color = color
  def render(self):
    if self.shape:
      drawPoly(self.shape.vertices, self.color)

class RenderStack (list):
  def render (self):
    for renderer in self:
      renderer.render()
    pygame.display.flip();

def nonOptimizedIterator (points):
  for p in points:
    yield (p, points)

def bucketPointIterator (points, divs):
  buckets = {}
  for point in points:
    bucketId = (int(point[0] * divs), int(point[1] * divs))
    if bucketId in buckets:
      buckets[bucketId].append(point)
    else:
      buckets[bucketId] = [point]

  for ((x, y), bucket) in buckets.items():
    adjacent_buckets = [bucket]
    if (x+1, y  ) in buckets: adjacent_buckets.append(buckets[(x+1, y  )])
    if (x-1, y  ) in buckets: adjacent_buckets.append(buckets[(x-1, y  )])
    if (x  , y+1) in buckets: adjacent_buckets.append(buckets[(x  , y+1)])
    if (x  , y-1) in buckets: adjacent_buckets.append(buckets[(x  , y-1)])
    if (x+1, y+1) in buckets: adjacent_buckets.append(buckets[(x+1, y+1)])
    if (x-1, y+1) in buckets: adjacent_buckets.append(buckets[(x-1, y+1)])
    if (x+1, y-1) in buckets: adjacent_buckets.append(buckets[(x+1, y-1)])
    if (x-1, y-1) in buckets: adjacent_buckets.append(buckets[(x-1, y-1)])
    for item in bucket:
      yield (item, itertools.chain.from_iterable(adjacent_buckets))

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

renderStack = RenderStack()
renderStack.append(ClearScreenRenderer(WHITE))
if ARGS.cell_optimization:
  renderStack.append(CellGridRenderer(ARGS.cell_optimization, ARGS.cell_optimization, CELL_LINE_COLOR))
renderStack.append(PointListRenderer(points, POINT_COLOR))
renderStack.append(ShapeListRenderer(shapes, LINE_COLOR))

def renderAndPause():
  if ARGS.animate:
    renderStack.render()
    if ARGS.interactive:
      waitForKey()
    else:
      waitForDelay()

renderAndPause()

pointIterator = (
  functools.partial(bucketPointIterator, divs=ARGS.cell_optimization) if ARGS.cell_optimization else
  nonOptimizedIterator
)

def inverseSquareRepulsion((px, py), (qx, qy)):
  delta_x = qx - px
  delta_y = qy - py
  invDistanceSquared = (delta_x*delta_x + delta_y*delta_y)**2
  return -delta_x * invDistanceSquared, -delta_y * invDistanceSquared

repulsion = inverseSquareRepulsion

# Relaxation
originalPointsRenderer = PointMovementRenderer([points], OTHER_POINT_COLOR)
renderStack.append(originalPointsRenderer)
for i in range(ARGS.relaxation_passes):
  originalPointsRenderer.point_list_list[:0] = [points[:]]
  points[:] = [
    vecAdd(
      p,
      vecMultiply(
        ARGS.relaxation_factor,
        vecSum([
          repulsion(p, q)
          for q in other_points
          if p != q
        #] + [
        #  repulsion(p, (-q[0], q[1]))
        #  for q in other_points
        #  if p != q
        #] + [
        #  repulsion(p, (q[0], -q[1]))
        #  for q in other_points
        #  if p != q
        #] + [
        #  repulsion(p, (2-q[0], q[1]))
        #  for q in other_points
        #  if p != q
        #] + [
        #  repulsion(p, (q[0], 2-q[1]))
        #  for q in other_points
        #  if p != q
        #] + [
        #  # Push points away from the container border by placing virtual,
        #  # mirror-image points on the other side of each boundary.
        #  repulsion(p, (-p[0], p[1])),
        #  repulsion(p, (2-p[0], p[1])),
        #  repulsion(p, (p[0], -p[1])),
        #  repulsion(p, (p[0], 2-p[1])),
        ])
      )
    )
    #for (p, other_points) in pointIterator(points)
    for (p, other_points) in nonOptimizedIterator(points)
  ]

  def rail(coord):
    return 0.0 if coord < 0.0 else 1.0 if coord > 1.0 else coord

  points[:] = [ (rail(point[0]), rail(point[1])) for point in points ]

  renderAndPause()

renderStack.remove(originalPointsRenderer)

activeShapeRenderer = ShapeRenderer(None, ACTIVE_LINE_COLOR)
renderStack.append(activeShapeRenderer)
activePointRenderer = PointRenderer(None, ACTIVE_POINT_COLOR)
renderStack.append(activePointRenderer)
consideringPointRenderer = PointRenderer(None, OTHER_POINT_COLOR)
renderStack.append(consideringPointRenderer)

for (p, other_points) in pointIterator(points):
  s = Shape(p)
  activePointRenderer.point = p
  activeShapeRenderer.shape = s
  for q in other_points:
    consideringPointRenderer.point = q
    if p != q:
      # Midpoint and slope of perpendicular bisector
      position = tuple((p + q) / 2.0 for (p, q) in zip(p, q))
      (dx, dy) = vecSubtract(q, p)
      slope    = (dy, -dx) # 90-degree counterclockwise rotation

      s.vertices = cutShape(s.core, s.vertices, position, slope)

      renderAndPause()

  shapes.append(s)

renderStack.remove(activeShapeRenderer)
renderStack.remove(activePointRenderer)
renderStack.remove(consideringPointRenderer)

if ARGS.profile:
  for (func, count) in call_counts.items():
    print "{}.{}: {}".format(func.__module__, func.__name__, count)

if ARGS.animate or ARGS.display:
  renderStack.render()
  waitForKey()
