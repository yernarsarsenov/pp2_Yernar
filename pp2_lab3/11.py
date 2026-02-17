class Pair:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self, another_pair):
        print(f"Result: {a + another_pair.a} {b + another_pair.b}")
    
a, b, a1, b1 = map(int, input().split())
obj = Pair(a, b)
obj1 = Pair(a1, b1)
obj.add(obj1)