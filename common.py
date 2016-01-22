#!/usr/bin/env python

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
  #   ⎡ a1x - a2x ⎤ = ⎡ (a1x - b1x)  (-a2x + b2x) ⎤⎡ t1 ⎤
  #   ⎣ a1y - a2y ⎦ = ⎣ (a1y - b1y)  (-a2y + b2y) ⎦⎣ t2 ⎦
  #
  # Shorten things up a little: (also cast to floats)
  d1y = a1y - b1y
  d1x = a1x - b1x
  d2x = a2x - b2x
  d2y = a2y - b2y
  dax = a1x - a2x
  day = a1y - a2y
  #   ⎡ dax ⎤ = ⎡ d1x  -d2x ⎤⎡ t1 ⎤
  #   ⎣ day ⎦ = ⎣ d1y  -d2y ⎦⎣ t2 ⎦
  # 
  # Inverse of 2x2 matrix:
  #                ⎡ a  b ⎤    ⎡  d -c ⎤            ⎡  d -c ⎤
  #   inv(A) = inv(⎣ c  d ⎦) = ⎣ -b  a ⎦ / det(A) = ⎣ -b  a ⎦ / (ad - bc)
  # 
  # In our case,
  #   det(A) = d1x * -d2y - d1y * -d2x
  #          = -d1x * d2y + d1y * d2x
  det = float(-d1x*d2y + d1y*d2x)
  if det == 0: return float('nan'), float('nan')
   
  # So, inv(A) =
  #   ⎡ -d2y/det  d2x/det ⎤
  #   ⎣ -d1y/det  d1x/det ⎦
  # 
  #   ⎡ t1 ⎤   ⎡ -d2y/det  d2x/det ⎤⎡ dax ⎤
  #   ⎣ t2 ⎦ = ⎣ -d1y/det  d1x/det ⎦⎣ day ⎦
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

def interpolateSegment(((x1, y1), (x2, y2)), t):
    return (x1 * (1-t) + x2 * t), (y1 * (1-t) + y2 * t)

def perpendicularBisector((x1, y1), (x2, y2)):


