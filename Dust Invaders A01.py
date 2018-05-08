# 
# ______ _   _ _____ _____   _   _____ _   _ _   _  ___ ______ ___________  _____ 
# |  _  \ | | /  ___|_   _/\| |/\_   _| \ | | | | |/ _ \|  _  \  ___| ___ \/  ___|
# | | | | | | \ `--.  | | \ ` ' / | | |  \| | | | / /_\ \ | | | |__ | |_/ /\ `--. 
# | | | | | | |`--. \ | ||_     _|| | | . ` | | | |  _  | | | |  __||    /  `--. \
# | |/ /| |_| /\__/ / | | / , . \_| |_| |\  \ \_/ / | | | |/ /| |___| |\ \ /\__/ /
# |___/  \___/\____/  \_/ \/|_|\/\___/\_| \_/\___/\_| |_/___/ \____/\_| \_|\____/ 
#                                                                                                                                                              
#
# Dust Invaders
# by Ilario Jeff Toniello
# https://github.com/ecodallaluna/dustinvaders  
#
# Version A.0.1 - Collect data usage (no display)
#
# Description
# =========================================================================
# This version of the app has the purpose of collecting info about the utilisation of a vacuum cleaner
# without the interaction with the game for statistical analysis. This app will silently storage the
# amount of usage of the vacuum cleaner by saving the movement of the accelerometer. Each 30 seconds 
# of usage will be saved as one "token". Other saved data are: time and kind of movement of the 
# vacuum cleaner on axes x and y (left/right up/down) 
#
# hardware requirement
# =========================================================================
# - micro:bit board microbit.org/
# - RTC (Real Time Clock) Board, this app is set for a DS3231 RCT Board
#
# software requirement
# =========================================================================
# this app was developed with Mu https://codewith.mu/
# with Mu or by command-line is possible to interact with the memory of the micro:bit board and save
# a copy of the usage data collected by the app
#
# !! WARNING !!
# =========================================================================
# every time the micro:bit is flashed ALL the files in the micro:bit
# are destroyed. Remember to download the usage date before that

#import microbit code library
from microbit import *

# set variables 
# =========================================================================
# set sensibility in milli-g
sensibility_sensor = 500
#set initial movement
mov_before = "-"
# set no 30s movement tokens
token = 0
# set image
check_led = Image("00000:00000:00500:00000:00000")


# list of functions
# =========================================================================

# functions to read time from DS3231 RTC (Real Time Clock) Board 

# To use the board is need to connect 4 pins from the board to the micro:bit
# - Connect GND on the breakout to GND on the microbit.
# - Connect VCC to 3V.
# - Connect SDA to pin 20.
# - Connect SCL to pin 19.

# functions to convert values for get_time()
# functions for RTC board from http://www.multiwingspan.co.uk

def bcd2dec(bcd):
    return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

def dec2bcd(dec):
    tens, units = divmod(dec, 10)
    return (tens << 4) + units
    
# this function reads time from the RTC board
# get_time() returns an arrey of int with information from RTC Board
# e.g. if called tm = get_time()
# tm[0] equal to hh 
    
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
    
# #set_time(0,0,12,5,1,4,2016), can be used set the time and date of RTC Board.
# The order of the numbers should be seconds, minutes, hours, week day, day, month, year.
# Needed to do just once to set time on the board, the stand alone battery will keep the clock working if micro:bit is turned off

def set_time(s,m,h,w,dd,mm,yy):
    t = bytes([s,m,h,w,dd,mm,yy-2000])
    for i in range(0,7):
        i2c.write(addr, bytes([i,dec2bcd(t[i])]), repeat=False)
    return

# check movement and report 
def is_moving(sens) :
    # read from accelerometer
    readx = accelerometer.get_x()
    ready = accelerometer.get_y()
    if readx > sens :
        result = "right"
    elif readx < -sens :
        result = "left"
    elif ready > sens :
        result = "up"
    elif ready < -sens :
        result = "down"
    else :
        result = "-"
    return result
    
# write function cicle of 30 sec that save all new movements
def capture_30s(sens) :
    # initialise variables
    time_sec = 0
    right_n = 0
    left_n = 0
    up_n = 0
    down_n = 0
    mov_before_cicle = "-"
    # set 30s acquisition data cicle
    while time_sec <= 30 :
        # get movement
        mov_into_cicle = is_moving(sens)
        # set inner if cicle to be sure to save only changes
        if mov_into_cicle != mov_before_cicle :
            mov_before_cicle = mov_into_cicle
            print("in  cicle "+ str(mov_into_cicle)) # just to check, remove from final
            display.show(check_led) # turn off led to show reading movement
            if mov_into_cicle == "right" :
                right_n = right_n + 1
            elif mov_into_cicle == "left" :
                left_n = left_n + 1
            elif mov_into_cicle == "up" :
                up_n = up_n + 1
            elif mov_into_cicle == "down" :
                down_n = down_n + 1
        sleep(500) # wait 0.5 sec before next reading
        display.clear() #turn off the led - the effect is a blick of 0.5 sec if a movement is detected
        time_sec = time_sec + 0.5 # advance time count
    # after 30s out of cicle, return data as arrey of int
    return [right_n, left_n, up_n, down_n]

 # function to storage data in txt file    
def save_data(time2save, token2save, r2save, l2save, u2save, d2save) :
    #create string to save
    string2save = str(time2save) + "\t" + str(token2save) + "\t" + str(r2save) + "\t" + str(l2save) + "\t" + str(u2save) + "\t" + str(d2save) + "\n"
    try :  # try to open existing file and copy data on saved_data
        with open('vacuum_data.txt', 'r') as my_file:
            saved_data = my_file.read()
    except OSError : # in case file do not exist create empty file and variable
        saved_data = "" 
        with open('vacuum_data.txt', 'w') as my_file:
            my_file.write("")
    #update data with new reading
    saved_data = saved_data + string2save
    print("saved data:") #just to chek, remove from final
    print(saved_data) #just to chek, remove from final
    #save new file with updated data
    with open('vacuum_data.txt', 'w') as my_file:
        my_file.write(saved_data)
    return


# start programme
# ===============================
 
while True :
    mov = is_moving(sensibility_sensor)
    if mov != mov_before :
        mov_before = mov
        token = token + 1 # token counter is updated
        print("identified movement! start cicle - " + mov_before) # remove from final
        data_30s = capture_30s(sensibility_sensor) #function 30s cicle + save movement
        print("token no: "+ str(token) + ", movements: R: " + str(data_30s[0]) + ", L: " + str(data_30s[1]) + ", U: " + str(data_30s[2]) + ", D: " + str(data_30s[3]) )    #this data will be saved in file in final version. Real time is still missing
        # read time
        time_now = running_time() # micro:bit internal time, MUST be update with RTC Board input
        #save data in file txt
        save_data(time_now, token, data_30s[0], data_30s[1], data_30s[2], data_30s[3]) 
    sleep(1000)