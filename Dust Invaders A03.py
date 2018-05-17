# Dust Invaders
# by Ilario Jeff Toniello
# https://github.com/ecodallaluna/dustinvaders  
#
# Version A.0.3 - Collect data usage (no display)
#
# Flash version without comments
# =========================================================================

from microbit import *

# set variables 
# =========================================================================
# set sensibility in milli-g
sensibility_sensor = 500
# set check image
check_led = Image("00000:00000:00500:00000:00000")

# other initial variables (do not change)
# =========================================================================
mov_before = "-"
token = 0
addr = 0x68
buf = bytearray(7)

# list of functions
# =========================================================================

# functions to read time from DS3231 RTC (Real Time Clock) Board 
def bcd2dec(bcd):
    return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

def dec2bcd(dec):
    tens, units = divmod(dec, 10)
    return (tens << 4) + units
    
def get_time():
    i2c.write(addr, b'\x00', repeat=False)
    buf = i2c.read(addr, 7, repeat=False)
    ss = bcd2dec(buf[0])
    mm = bcd2dec(buf[1])
    if buf[2] & 0x40:
        hh = bcd2dec(buf[2] & 0x1f)
        if buf[2] & 0x20:
            hh += 12
    else:
        hh = bcd2dec(buf[2])
    wday = buf[3]
    DD = bcd2dec(buf[4])
    MM = bcd2dec(buf[5] & 0x1f)
    YY = bcd2dec(buf[6])+2000
    return [hh,mm,ss,YY,MM,DD,wday]
    
# the function set_time(0,0,12,5,1,4,2016) can be used set the time and date of RTC Board
def set_time(s,m,h,w,dd,mm,yy):
    t = bytes([s,m,h,w,dd,mm,yy-2000])
    for i in range(0,7):
        i2c.write(addr, bytes([i,dec2bcd(t[i])]), repeat=False)
    return

# check movement and report 
def is_moving(sens) :
    readx = accelerometer.get_x()
    ready = accelerometer.get_y()
    if readx > sens :
        result = "r"
    elif readx < -sens :
        result = "l"
    elif ready > sens :
        result = "u"
    elif ready < -sens :
        result = "d"
    else :
        result = "-"
    return result

#capture 30s of vacuum activity
def capture_30s(sens) :
    time_sec = 0
    right_n = 0
    left_n = 0
    up_n = 0
    down_n = 0
    mov_before_cicle = "-"
    while time_sec <= 30 :
        mov_into_cicle = is_moving(sens)
        if mov_into_cicle != mov_before_cicle :
            mov_before_cicle = mov_into_cicle
            display.show(check_led)
            if mov_into_cicle == "r" :
                right_n += 1
            elif mov_into_cicle == "l" :
                left_n += 1
            elif mov_into_cicle == "u" :
                up_n += 1
            elif mov_into_cicle == "d" :
                down_n += 1
        sleep(500)
        display.clear()
        time_sec += 0.5
    return [right_n, left_n, up_n, down_n]

# function to storage data in txt file    
def save_data(time2save, token2save, r2save, l2save, u2save, d2save) :
    time2save_string = str(time2save[3]) + "-" + str(time2save[4]) + "-" + str(time2save[5]) + "\t" + str(time2save[0]) + ":" + str(time2save[1]) + ":" + str(time2save[2]) + "\t" + str(time2save[6])
    string2save = time2save_string + "\t" + str(token2save) + "\t" + str(r2save) + "\t" + str(l2save) + "\t" + str(u2save) + "\t" + str(d2save) + "\n"
    try :  
        with open('vacuum_data.txt', 'r') as my_file:
            saved_data = my_file.read()
    except OSError : 
        saved_data = "" 
        with open('vacuum_data.txt', 'w') as my_file:
            my_file.write("")
    saved_data = saved_data + string2save
    print("saved data:")
    print(saved_data)
    with open('vacuum_data.txt', 'w') as my_file:
        my_file.write(saved_data)
    return

# start programme
# ===============================
 
while True :
    mov = is_moving(sensibility_sensor)
    if mov != mov_before :
        mov_before = mov
        token += 1
        data_30s = capture_30s(sensibility_sensor)
        time_now = get_time()
        save_data(time_now, token, data_30s[0], data_30s[1], data_30s[2], data_30s[3]) 
    sleep(1000)