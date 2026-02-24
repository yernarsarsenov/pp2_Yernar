#shortest path around circle
import math

def intersects(r, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    a = dx*dx + dy*dy
    b = 2*(x1*dx + y1*dy)
    c = x1*x1 + y1*y1 - r*r
    disc = b*b - 4*a*c
    if disc < 0:
        return False
    t1 = max(0.0, (-b - math.sqrt(disc)) / (2*a))
    t2 = min(1.0, (-b + math.sqrt(disc)) / (2*a))
    return t2 > t1

def shortest_path(r, x1, y1, x2, y2):
    length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    if not intersects(r, x1, y1, x2, y2):
        return length
    ao = math.sqrt(x1*x1 + y1*y1)
    bo = math.sqrt(x2*x2 + y2*y2)
    alpha = math.acos(r / ao)
    beta  = math.acos(r / bo)
    gamma = math.acos((x1*x2 + y1*y2) / (ao*bo))
    return math.sqrt(ao*ao - r*r) + math.sqrt(bo*bo - r*r) + r*(gamma - alpha - beta)

r = int(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())
print(f"{shortest_path(r, x1, y1, x2, y2):.10f}")