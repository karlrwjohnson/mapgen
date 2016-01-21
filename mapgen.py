#!/usr/bin/env python

import argparse
import itertools
import random
import sys

PARSER = argparse.ArgumentParser(description='Delaunay Triangulation Generator')
PARSER.add_argument('--num_points', default=20, type=int, help='Number of random points to generate')
PARSER.add_argument('--animate', action='store_true', help='Animate the segment consideration algorithm')
PARSER.add_argument('--interactive', action='store_true', help='Pause after every segment consideration (requires --interactive)')
PARSER.add_argument('--delay', default=50, type=int, help='Time to show each frame, in milliseconds (requires --animate)')
PARSER.add_argument('--report_call_counts', action='store_true', help='Report how many times intersection() and addSegment() are called')
ARGS = PARSER.parse_args()

SIZE = 800, 800
RED = 255,0,0
PINK = 255,200,200
LAVENDER = 200,200,255
GOLD = 200,200,0
GREEN = 0,200,0
BLUE = 0,0,255
BLACK = 0,0,0
WHITE = 255,255,255
GRAY = 180,180,180
POINT_COLOR = BLUE
LINE_COLOR = GREEN
LINE_INVALIDATED = PINK
LINE_ERROR = RED
LINE_NEVER_VALID = LAVENDER
LINE_HIGHLIGHT = GOLD
POINT_RADIUS = 5
LINE_WIDTH = 1

if ARGS.animate:
  import pygame

  pygame.init()
  screen = pygame.display.set_mode(SIZE)
  surf = pygame.display.get_surface()

call_counts = {
  'intersection': 0,
  'addSegment': 0,
}

def intersection (((a1x, a1y), (b1x, b1y)), ((a2x, a2y), (b2x, b2y))):
  """Determine where, if ever, two segments defined by their endpoints intersect

  Parameters: Two pairs of points, where each point is a pair of numbers

  Return: Pair of floats containing the relative weights of each pair of numbers
    where the intersection occurs on the segment

          t2=0           .b1 t1=1
              a2     _.-'   
                \_.-'       
             _.-'\           segment 1 = (a1, b1)
          .-'     \          segment 2 = (a2, b2)
       a1'         b2       
      t1=0          t2=1
  """
  call_counts['intersection'] += 1

  # Define a parametric system of equations f1(t) and f2(t) where 0<=t<=1
  #   f(t) = a * (1 - t) + b * t = a + (b - a) * t
  # 
  # Set them equal to each other and solve for t.
  #
  #   f1(t1) = f2(t2)
  #   a1 + (-a1 + b1) * t1 = a2 + (-a2 + b2) * t2
  #   (a1 - a2) = (a1 - b1) * t1 + (-a2 + b2) * t2
  # 
  #   (a1x - a2x) = (a1x - b1x) * t1 + (-a2x + b2x) * t2
  #   (a1y - a2y) = (a1y - b1y) * t1 + (-a2y + b2y) * t2
  # 
  #   [ a1x - a2x ] = [ (a1x - b1x)  (-a2x + b2x) ][ t1 ]
  #   [ a1y - a2y ] = [ (a1y - b1y)  (-a2y + b2y) ][ t2 ]
  #
  # Shorten things up a little: (also cast to floats)
  d1y = a1y - b1y
  d1x = a1x - b1x
  d2x = a2x - b2x
  d2y = a2y - b2y
  dax = a1x - a2x
  day = a1y - a2y
  #   [ dax ] = [ d1x  -d2x ][ t1 ]
  #   [ day ] = [ d1y  -d2y ][ t2 ]
  # 
  # Inverse of 2x2 matrix:
  #                [ a  b ]    [  d -c ]            [  d -c ]
  #   inv(A) = inv([ c  d ]) = [ -b  a ] / det(A) = [ -b  a ] / (ad - bc)
  # 
  # In our case,
  #   det(A) = d1x * -d2y - d1y * -d2x
  #          = -d1x * d2y + d1y * d2x
  det = float(-d1x*d2y + d1y*d2x)
  if det == 0: return float('nan'), float('nan')
  # 
  # So, inv(A) =
  #   [ -d2y/det  d2x/det ]
  #   [ -d1y/det  d1x/det ]
  # 
  #   [ t1 ] = [ -d2y/det  d2x/det ][ dax ]
  #   [ t2 ] = [ -d1y/det  d1x/det ][ day ]
  t1 = ( -d2y*dax + d2x*day ) / det
  t2 = ( -d1y*dax + d1x*day ) / det

  return t1, t2

assert(intersection( ((1,1),(2,2)), ((2,1),(1,2)) ) == (0.5,0.5))
assert(intersection( ((3,1),(3,4)), ((1,2),(4,2)) ) == (1.0/3,2.0/3))


def segmentsIntersect ((a1, b1), (a2, b2)):
  if a1 == a2 or a1 == b2 or b1 == a2 or b1 == b2:
    return False
  t1, t2 = intersection((a1, b1), (a2, b2))
  return 0 <= t1 and t1 <= 1 and 0 <= t2 and t2 <= 1

assert(segmentsIntersect( ((1,1),(2,2)), ((2,1),(1,2)) ))
assert(segmentsIntersect( ((3,1),(3,4)), ((1,2),(4,2)) ))
assert(not segmentsIntersect( ((1,1),(1,2)), ((2,1),(2,2)) ))
assert(not segmentsIntersect( ((2,2),(3,3)), ((2,1),(1,2)) ))
assert(not segmentsIntersect( ((1,1),(1,2)), ((1,1),(2,1)) ))


def segmentCompare(((a1x, a1y), (b1x, b1y)), ((a2x, a2y), (b2x, b2y))):
  d1x = a1x - b1x
  d1y = a1y - b1y
  d2x = a2x - b2x
  d2y = a2y - b2y
  return cmp(d1x*d1x + d1y*d1y, d2x*d2x + d2y*d2y)

assert(segmentCompare( ((1,1),(2,2)), ((2,1),(1,2)) ) == 0)
assert(segmentCompare( ((1,1),(3,3)), ((2,1),(1,2)) ) > 0)
assert(segmentCompare( ((1,1),(3,3)), ((1,4),(4,1)) ) < 0)

def addSegment (newSegment):
  call_counts['addSegment'] += 1

  dooming = []
  doomedBy = []

  highlighted_segments[:] = [newSegment]

  for existing in accepted_segments:
    if segmentsIntersect(newSegment, existing):
      if segmentCompare(newSegment, existing) <= 0:
        dooming.append(existing)
      else:
        doomedBy.append(existing)

  error_segments_tmp1[:] = dooming
  error_segments_tmp2[:] = doomedBy

  for doomed in dooming:
    accepted_segments.remove(doomed)
    invalidated_segments.append(doomed)

  if not len(doomedBy):
    accepted_segments.append(newSegment)

  if ARGS.animate:
    render()
    if ARGS.interactive:
      waitForKey()
    else:
      waitForDelay()


points = [
  (random.random(), random.random())
  for i in range(ARGS.num_points)
]

accepted_segments = []
invalidated_segments = []
never_valid_segments = []
highlighted_segments = []
error_segments = []
error_segments_tmp1 = []
error_segments_tmp2 = []

def screenCoord(point):
  try:
    return int(point[0] * SIZE[0]), int(point[1] * SIZE[1])
  except e:
    print "param was {}".format(point)
    raise e

def drawSegment(segment, color):
  pygame.draw.line(surf, color, screenCoord(segment[0]), screenCoord(segment[1]), 2)

def render ():
  screen.fill(WHITE);
  for point in points:
    pygame.draw.circle(surf, POINT_COLOR, screenCoord(point), POINT_RADIUS)
  for segment in never_valid_segments:
    drawSegment(segment, LINE_NEVER_VALID)
  for segment in invalidated_segments:
    drawSegment(segment, LINE_INVALIDATED)
  for segment in error_segments:
    drawSegment(segment, LINE_ERROR)
  for segment in accepted_segments:
    drawSegment(segment, LINE_COLOR)
  for segment in highlighted_segments:
    drawSegment(segment, LINE_HIGHLIGHT)
  for segment in error_segments_tmp1:
    drawSegment(segment, LINE_NEVER_VALID)
  for segment in error_segments_tmp2:
    drawSegment(segment, LINE_INVALIDATED)

  pygame.display.flip();

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
  pygame.time.wait(ARGS.delay);
  for event in pygame.event.get():
    if event.type == pygame.QUIT or \
       (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
      sys.exit()

for a, b in itertools.combinations(points, 2):
  addSegment((a, b))

  highlighted_segments = []
  error_segments_tmp1 = []
  error_segments_tmp2 = []

  if ARGS.animate:
    render()
    if ARGS.interactive:
      waitForKey()
    else:
      waitForDelay()

print "Call counts:"
for (method, times) in call_counts.items():
  print " - {}: {}".format(method, times)

if ARGS.animate:
  render()
  waitForKey()
