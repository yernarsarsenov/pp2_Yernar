import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def show(self):
        print(f"({self.x}, {self.y})")

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
    
    def dist(self, another_point):
        return math.sqrt((self.x - another_point.x) ** 2 
                        + (self.y - another_point.y) ** 2)

x, y = map(int, input().split())
new_x, new_y = map(int, input().split())
x2, y2 = map(int, input().split())
obj2 = Point(x2, y2)

obj = Point(x, y)
obj.show()

obj.move(new_x, new_y)
obj.show()

print(f"{obj.dist(obj2):.2f}")