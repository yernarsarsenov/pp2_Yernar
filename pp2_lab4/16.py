#long duration time zones
import datetime

def parse_time(s):
    date, time, time_zone = s.split()
    dt = datetime.datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S")
    sign = 1
    if time_zone[3] == '-':
        sign = -1
    
    h = int(time_zone[4:6])
    m = int(time_zone[7:9])

    return dt - datetime.timedelta(hours=h, minutes=m) * sign

a = input()
b = input()

a_utc = parse_time(a)
b_utc = parse_time(b)

duration = int((b_utc - a_utc).total_seconds())
print(duration)