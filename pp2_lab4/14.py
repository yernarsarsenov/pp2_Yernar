#days between time zones
import datetime
def parse_time(a):
    date, time = a.split()
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    sign = 0
    if time[3] == '+':
        sign = 1
    else:
        sign = -1
    h = int(time[4:6])
    m = int(time[7:9])

    return dt - datetime.timedelta(hours=h, minutes=m) * sign

a1 = input()
a2 = input()

t1 = parse_time(a1)
t2 = parse_time(a2)
diff_seconds = abs((t1 - t2).total_seconds())
days = int(diff_seconds / 86400)

print(days)