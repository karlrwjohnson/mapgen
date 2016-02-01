#!/usr/bin/env python
# -*- coding: utf-8 -*-
from debug import *

NaN = float('NaN')

def intersection (((a0x, a0y), (a1x, a1y)), ((b0x, b0y), (b1x, b1y))):
  """Determine where, if ever, two segments defined by their endpoints intersect

  Parameters: Two pairs of points, where each point is a pair of numbers

  Return: Pair of floats containing the relative weights of each pair of numbers
    where the intersection occurs on the segment

          tb=0           .a1 ta=1
              b0     _.-'   
                \_.-'       
             _.-'\           segment a = (a0, a1)
          .-'     \          segment b = (b0, b1)
       a0'         b1       
      ta=0          tb=1
  """

  # Define a parametric system of equations f1(t) and f2(t) where 0<=t<=1
  #   segment(t) = p0 * (1 - t) + p1 * t = p0 + (-p0 + p1) * t
  # 
  # Set them equal to each other and solve for t.
  #
  #   segment_a(ta) = segment_b(tb)
  #   a0 + (-a0 + a1) * ta = b0 + (-b0 + b1) * tb
  #   (a0 - b0) = (a0 - a1) * ta + (-b0 + b1) * tb
  # 
  #   (a0x - b0x) = (a0x - a1x) * ta + (-b0x + b1x) * tb
  #   (a0y - b0y) = (a0y - a1y) * ta + (-b0y + b1y) * tb
  # 
  #   ⎡ a0x - b0x ⎤ = ⎡ (a0x - a1x)  (-b0x + b1x) ⎤⎡ ta ⎤
  #   ⎣ a0y - b0y ⎦ = ⎣ (a0y - a1y)  (-b0y + b1y) ⎦⎣ tb ⎦
  #
  # Shorten things up a little:
  adx = a0x - a1x
  ady = a0y - a1y
  bdx = b0x - b1x
  bdy = b0y - b1y
  d0x = a0x - b0x
  d0y = a0y - b0y
  #   ⎡ d0x ⎤ = ⎡ adx  -bdx ⎤⎡ ta ⎤
  #   ⎣ d0y ⎦ = ⎣ ady  -bdy ⎦⎣ tb ⎦
  # 
  # Inverse of 2x2 matrix:
  #                ⎡ a  b ⎤    ⎡  d -c ⎤            ⎡  d -c ⎤
  #   inv(A) = inv(⎣ c  d ⎦) = ⎣ -b  a ⎦ / det(A) = ⎣ -b  a ⎦ / (ad - bc)
  # 
  # In our case,
  #   det(A) = adx * -bdy - ady * -bdx
  #          = -adx * bdy + ady * bdx
  det = -adx*bdy + ady*bdx
  if det == 0: return NaN, NaN
   
  # So, inv(A) =
  #   ⎡ -bdy/det  bdx/det ⎤
  #   ⎣ -ady/det  adx/det ⎦
  # 
  #   ⎡ ta ⎤   ⎡ -bdy/det  bdx/det ⎤⎡ d0x ⎤
  #   ⎣ tb ⎦ = ⎣ -ady/det  adx/det ⎦⎣ d0y ⎦
  ta = float( -bdy*d0x + bdx*d0y ) / det
  tb = float( -ady*d0x + adx*d0y ) / det

  return ta, tb

assertEqual(intersection( ((1,1),(2,2)), ((2,1),(1,2)) ), (0.5,0.5))
assertEqual(intersection( ((3,1),(3,4)), ((1,2),(4,2)) ), (1.0/3,2.0/3))


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

@profile
def interpolateSegment(((x1, y1), (x2, y2)), t):
  return (x1 * (1-t) + x2 * t), (y1 * (1-t) + y2 * t)

def perpendicularBisector((x1, y1), (x2, y2), ((xmin, xmax),(ymin,ymax))=((0,1),(0,1))):
  """Calculate the perpendicular bisector of a segment.

  Given two points, find the endpoints of the perpendicular bisector of a
  segment connecting those points. The perpendicular bisector's endpoints are
  bounded by the extents of the specified rectangle (the unit square by default)

  The order of the returned endpoints is unrelated to the positions of the
  original points.
  """
  dx = x2 - x1
  dy = y2 - y1

  if dx == 0:
    if dy == 0:
      raise RuntimeError("Start and end points are both ({}, {}".format(x1, y1))
    else:
      # Points are vertically aligned
      return (x1, ymin), (x2, ymax)
  else:
    if dy == 0:
      # Points are horizontally aligned
      return (xmin, y1), (xmax, y2)
    else:
      # The midpoint. The bisector must pass through it.
      xmid = (x1 + x2) * 0.5
      ymid = (y1 + y2) * 0.5

      # Points along the segment satisfy the parametric equation
      #   (x, y) = (dx, dy) * t + (xmid, ymid)
      # where t = -0.5 @ (x1, y1)
      #       t = +0.5 @ (x2, y2)
      #   and t =  0   @ the midpoint (xmid, ymid)
      #
      # (If this looks confusing, think of y=mx+b from Algebra 1, but
      # using 't' instead of 'x' and vectors for 'y', 'm', and 'b'.
      # In fact, let's define m = (dx, dy) and b = (xmid, ymid):)
      #   (x, y) = m * t + b
      #
      # The perpendicular bisector uses a similar equation, but the "slope" m is
      # rotated by 90 degrees. The dx and dy components are switched and one is
      # negated. (The direction of rotation determines which term is negated,
      # but is unimportant for our purposes.)
      #   m' = (-dy, dx)
      #
      # Solve for t.
      #   (x, y) = m' * t + b
      #   m' * t = (x, y) - b
      #       (x, y) - b
      #   t = ----------
      #           m'
      #
      # Expand out m' and b again.
      #       (x, y) - (xmid, ymid)
      #   t = --------------------- 
      #            (-dy, dx)
      #
      # The parametric equation can be rewritten as two separate equations.
      # Since the LHS of each equals 't', the RHS's equal each other.
      #       y - ymid   x - xmid
      #   t = -------- = --------
      #         -dy         dx
      #
      # Now, one can solve for x and y directly
      #   y = (x - xmid) * (-dy) / ( dx) + ymid
      #   x = (y - ymid) * ( dx) / (-dy) + xmid
      #
      # The segment intersects the rectangle's borders where x or y is set
      # equal to xmin, xmax, ymin, and ymax.
      intercepts = [
        (xmin, (xmin - xmid) * -dy / dx + ymid),
        (xmax, (xmax - xmid) * -dy / dx + ymid),
        ((ymin - ymid) * dx / -dy + xmid, ymin),
        ((ymax - ymid) * dx / -dy + xmid, ymax),
      ]

      # Although the segment intersects the bounding box in four places, only
      # the middle two define the segment's endpoints within it.
      #          ▄▀ ▀▄         ▀▄┌──────┐ ┌──────┐▄▀                  
      #    ┌───▄▀─┐ ┌─▀▄───┐     ▀▄     │ │     ▄▀          █ █       
      #    │ ▄▀   │ │   ▀▄ │     │ ▀▄   │ │   ▄▀ │         █   █      
      #    ▄▀     │ │     ▀▄     └───▀▄─┘ └─▄▀───┘   ┌────█─┐ ┌─█────┐
      #  ▄▀└──────┘ └──────┘▀▄         ▀▄ ▄▀         │   █  │ │  █   │
      #                                              │  █   │ │   █  │
      #           ┌──────┐▄▄▀▀ ▀▀▄▄┌──────┐          └─█────┘ └────█─┘
      #           │   ▄▄▀▀         ▀▀▄▄   │           █             █ 
      #           ▄▄▀▀   │         │   ▀▀▄▄          █               █
      #       ▄▄▀▀└──────┘         └──────┘▀▀▄▄                       
      #
      # If we tell Python to sort the array of intercepts, it will
      # automatically put them in the order of their x coordinates.
      # The middle two elements of that array will be the intercepts
      # we want.
      intercepts.sort()
      return intercepts[1], intercepts[2]

def segmentsEquivalent((p1, p2), (q1, q2)):
  return (p1 == q1 and p2 == q2) or (p1 == q2 and p2 == q1)

assert(segmentsEquivalent( perpendicularBisector((0,0),(1,1)), ((1,0), (0,1)) ))
assert(segmentsEquivalent( perpendicularBisector((1,1),(0,0)), ((1,0), (0,1)) ))
assert(segmentsEquivalent( perpendicularBisector((1,0),(0,1)), ((1,1), (0,0)) ))
assert(segmentsEquivalent( perpendicularBisector((0,1),(1,0)), ((1,1), (0,0)) ))

def vecSubtract((x1, y1), (x2, y2)):
  return (x1 - x2), (y1 - y2)

@debug
def crossProduct((x1, y1), (x2, y2)):
  #                                 ⎛⎡ i   j   k ⎤⎞
  # (x1, y1, 0) x (x2, y2, 0) = det ⎜⎢ x1  y1  0 ⎥⎟ 
  #                                 ⎝⎣ x2  y2  0 ⎦⎠
  #
  # = i*(y1*0 - y2*0) + j*(0*x2 - 0*x2) + k*(x1*y2 - x2*y1)
  #
  #   ⎡       0       ⎤
  # = ⎢       0       ⎥
  #   ⎣ x1*y2 - x2*y1 ⎦
  #
  return x1 * y2 - x2 * y1

def slice(segment1, segment2, point):
  t1, t2 = intersection(segment1, segment2)
  intersect = interpolate(segment1, t1)

@profile
def segmentAndLineIntersection(((x0, y0),(x1, y1)), (xc, yc), (mx, my)):
  """
  Given a segment and a line in point-slope format, calculate where -- if ever,
  the line intersects the segment.

  Parameters:
    ((x0, y0),(x1, y1)) -- endpoints of segment
    (xc, yc) -- point through which the line passes
    (mx, my) -- vector parallel to the line

  Return: The value `t` which can be used to determine where the line intersects
    the segment:
    - If t = 0, the line intersects the segment at p0.
    - If t = 1, the line intersects the segment at p1.
    - If 0 < t < 1, the line intersects the segment between p0 and p1. To obtain
      the exact coordinates, use the equation
          p(t) = p0 * (1 - t) + p1 * t
    - If t < 0 or t > 1, the line does not intersect the segment, but it WOULD
      if segment extended farther in that direction.
    - If t = NaN, the line and segment are parallel.
  """
  # Though the equation is simple, its derivation is math-heavy.
  #
  #   p0 = (x0, y0)
  #   p1 = (x1, y1)
  #   pc = (xc, yc)
  #
  # Construct parametric equations describing the path along the segment and line:
  #   segment(t) = p0 * (1 - t) + p1 * t
  #      line(t) = pc + m * t
  #
  #                segment(t1) = line(t2)
  #    p0 * (1 - t1) + p1 * t1 = pc + m * t2
  #       p0 + (-p0 + p1) * t1 = pc + m * t2
  #   (-p0 + p1) * t1 - m * t2 = -p0 + pc
  #    (p0 - p1) * t1 + m * t2 = p0 - pc
  #  
  #   (x0 - x1) * t1 + mx * t2 = x0 - xc
  #   (y0 - y1) * t1 + my * t2 = y0 - yc
  # 
  #    ⎡ (x0 - x1)  mx ⎤⎡ t1 ⎤   ⎡ (x0 - xc) ⎤
  #    ⎣ (y0 - y1)  my ⎦⎣ t2 ⎦ = ⎣ (y0 - yc) ⎦
  #
  # Inverse of 2x2 matrix:
  #                ⎡ a  b ⎤    ⎡  d -c ⎤            ⎡  d -c ⎤
  #   inv(A) = inv(⎣ c  d ⎦) = ⎣ -b  a ⎦ / det(A) = ⎣ -b  a ⎦ / (ad - bc)
  #
  #   det = my * (x0 - x1) - mx * (y0 - y1)
  #
  #   ⎡ t1 ⎤   ⎡     my         -mx    ⎤⎡ (x0 - xc) ⎤
  #   ⎣ t2 ⎦ = ⎣ (-y0 + y1)  (x0 - x1) ⎦⎣ (y0 - yc) ⎦ / det
  #
  # Since we only care where the segment is intersected (the line is infinitely
  # long), we only need to solve for t1.
  #
  #        my * (x0 - xc) - mx * (y0 - yc)
  #   t1 = -------------------------------
  #        my * (x0 - x1) - mx * (y0 - y1)
  numerator   = my * (x0 - xc) - mx * (y0 - yc)
  denominator = my * (x0 - x1) - mx * (y0 - y1)

  if denominator == 0:
    return NaN
  else:
    return numerator / float(denominator)

assertEqual(segmentAndLineIntersection( ((0,0),(1,0)), (0.5,1), (0,1) ),  0.5)
assertEqual(segmentAndLineIntersection( ((0,0),(0,1)), (1,0.5), (1,0) ),  0.5)
assertEqual(segmentAndLineIntersection( ((0,0),(1,1)), (1,0), (1,0) ),    0.0)
assertEqual(segmentAndLineIntersection( ((0,0),(1,1)), (1,0), (0,1) ),    1.0)
assertEqual(str(segmentAndLineIntersection( ((0,0),(1,0)), (0,1), (1,0) )), str(NaN))
assertEqual(segmentAndLineIntersection( ((0,0),(1,0)), (0.5,0.5), (1,2) ),0.25)
assertEqual(segmentAndLineIntersection( ((1,1),(2,3)), (2,2), (1,0) ),    0.5)
assertEqual(segmentAndLineIntersection( ((1,1),(2,3)), (2,1), (1,-2) ),   0.5)
assertEqual(segmentAndLineIntersection( ((0,4),(4,0)), (0,0), (1,1) ),    0.5)

@profile
def cutShape(center, vertices, midpoint, slopeVector):

  class Object (object):
    def __init__(self, **kwargs):
      self.__dict__.update(kwargs)
    def __repr__(self):
      return repr(self.__dict__)

  intersections = []
  for index in range(len(vertices)):
    start = vertices[index]
    end   = vertices[index + 1] if index + 1 < len(vertices) else vertices[0]
    t = segmentAndLineIntersection((start, end), midpoint, slopeVector)

    if t >= 0 and t <= 1:
      intercept = interpolateSegment((start, end), t)
      intersections.append(Object(
        intercept=intercept,
        startIndex=index,
        endIndex=index + 1,
      ))

  def circularSlice(list, start, end):
    return (list[start:end+1] if (end >= start) else
            list[start:] + list[:end+1])

  # Assuming the vertices form a closed, convex polygon, a line would either
  # intersect it in two places (in and out), or not at all.
  if len(intersections) == 0:
    # Shape is returned unchanged
    return vertices
  elif len(intersections) == 2:
    # Determine the relative order of the intersections relative to the center
    # using the cross product. The right-hand rule says that the cross product
    # will be positive if the LHS vector is clockwise relative to the RHS vector
    #
    #   counterclockwise     
    #       \▄▀▄   ↺         
    #      ▄▀\↖ ▀▄           
    #    ▄▀ ↓ \   ▀▄         
    #   █   ↓ ↺\    █        
    #    █  X↘  \↖ █         
    #     █     ↘\█    ↻     
    #      █▄▄▄▄▄█\ clockwise
    #
    (clockwise, counterclockwise) = (
      (intersections[0], intersections[1])
      if crossProduct(
        vecSubtract(intersections[0].intercept, center),
        vecSubtract(intersections[1].intercept, center)) > 0
      else (intersections[1], intersections[0])
    )

    return (
      [counterclockwise.intercept] +
      circularSlice(vertices, counterclockwise.endIndex, clockwise.startIndex) +
      [clockwise.intercept]
    )

  else:
    assert False, (
      ("Somehow, line @ position {}, slope {} intersects " +
      "supposedly-convex shape {} in {} places:\n{}").format(
        midpoint, slopeVector, vertices, len(intersections), intersections
      )
    )


