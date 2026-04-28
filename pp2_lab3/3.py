def to_int(word):
    nums = {'ONE':'1', 'TWO':'2', 'THR':'3', 'FOU':'4', 'FIV':'5',
            'SIX':'6', 'SEV':'7', 'EIG':'8', 'NIN':'9', 'ZER':'0'}
    return nums[word]

def to_str(digit):
    words = {'1':'ONE', '2':'TWO', '3':'THR', '4':'FOU', '5':'FIV',
             '6':'SIX', '7':'SEV', '8':'EIG', '9':'NIN', '0':'ZER', '-':'MIN'}
    return words[digit]
    
number = input()

for op in "+-*":
    if op in number:
        a, b = number.split(op)
        break
    
num_a = ""
for i in range(0, len(a), 3):
    num_a += to_int(a[i:i+3])
    
num_b = ""
for i in range(0, len(b), 3):
    num_b += to_int(b[i:i+3])

if op == "+":
    result = int(num_a) + int(num_b)
elif op == "-":
    result = int(num_a) - int(num_b)
elif op == "*":
    result = int(num_a) * int(num_b)

for digit in str(result):
    print(to_str(digit), end="")