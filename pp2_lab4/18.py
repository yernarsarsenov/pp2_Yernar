#mirror reflection
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

k = (-y2 - y1) / (x2 - x1)
b = y1 - k * x1

x = -b / k
print(f"{x:.10f} {0.0:.10f}")
