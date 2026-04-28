#module query engine 
import importlib
import importlib.util

q = int(input())
for i in range(q):
    my_module, my_attr = input().split()

    try:
        module = importlib.import_module(my_module)
    except Exception:
        print("MODULE_NOT_FOUND")
        continue


    module = importlib.import_module(my_module)
    
    if not hasattr(module, my_attr):
        print("ATTRIBUTE_NOT_FOUND")
        continue
    else:
        attr = getattr(module, my_attr)
        if callable(attr):
            print("CALLABLE")
        else:
            print("VALUE")