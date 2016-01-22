#!/usr/bin/env python

import argparse
import itertools
import json
import random
import sys

PARSER = argparse.ArgumentParser(description='Voroni Diagram Generator')
PARSER.add_argument('--num_points', default=20, type=int, help='Number of random points to generate')
PARSER.add_argument('--animate', action='store_true', help='Animate the segment consideration algorithm')
PARSER.add_argument('--interactive', action='store_true', help='Pause after every segment consideration (requires --interactive)')
PARSER.add_argument('--delay', default=50, type=int, help='Time to show each frame, in milliseconds (requires --animate)')
PARSER.add_argument('--report_call_counts', action='store_true', help='Report how many times intersection() and addSegment() are called')
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

accepted_segments = []
invalidated_segments = []
never_valid_segments = []
highlighted_segments = []
error_segments = []
error_segments_tmp1 = []
error_segments_tmp2 = []


class Point (object):
    def __init__(self, coords):
        self.coords = coords
        self.edges = list()

def perpendicularBisector((x1, y1), (x2, y2)):



added_points = []
edges = []
def addPoint(coords):
    new_point = Point(coords)
    if len(added_points) >= 1:
        for added_point in added_points:
            new_segment = (new_point, added_point)
            for segment in 

    added_points.append(new_point)

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
