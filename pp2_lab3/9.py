class Circle:
    def __init__(self, radius, pi = 3.14159):
        self.radius = radius
        self.pi = pi
    
    def area(self):
        return self.pi * self.radius ** 2
    
r = int(input())
obj = Circle(r)
print(f"{obj.area():.2f}")