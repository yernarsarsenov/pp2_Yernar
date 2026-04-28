#radar coverage
import math

def segment_in_circle(R, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    a = dx*dx + dy*dy
    b = 2 * (x1*dx + y1*dy)
    c = x1*x1 + y1*y1 - R*R
    
    disc = b ** 2 - 4*a*c
    if disc < 0 or a == 0:
        return 0.0
    
    t1 = max(0.0, (-b - math.sqrt(disc)) / (2*a))
    t2 = min(1.0, (-b + math.sqrt(disc)) / (2*a))
    
    return max(0.0, (t2 - t1) * math.sqrt(a))

R = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())
print(f"{segment_in_circle(R, x1, y1, x2, y2):.10f}")