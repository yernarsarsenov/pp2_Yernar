#next birthday time zones
import datetime

def is_leap_year(a):
    return (a % 400 == 0) or (a % 4 == 0 and a % 100 != 0)

def parse_time(s):
    date, tz = s.split()
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    sign = 1 
    if tz == '-':
        sign = -1
        
    h = int(tz[4:6])
    m = int(tz[7:9])
    return dt - datetime.timedelta(hours=h, minutes=m) * sign

a = input() 
b = input()

current_utc = parse_time(b)

birth_month = int(a[5:7])
birth_day = int(a[8:10])
birth_tz = a.split()[1]

current_year = int(b[:4])

def birthday_utc(year):
    day = birth_day
    if birth_month == 2 and birth_day == 29 and not is_leap_year(year):
        day = 28
    s = f"{year:04d}-{birth_month:02d}-{day:02d} {birth_tz}"
    return parse_time(s)

bday = birthday_utc(current_year)
if bday < current_utc:
    bday = birthday_utc(current_year + 1)
    
sec = int((bday - current_utc).total_seconds())
ans = 0 
if sec > 0 :
    ans =  (sec + 86400 - 1 ) // 86400
print(ans)