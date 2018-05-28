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
# Version C.0.1 - Game  
#
# Description
# =========================================================================
# This version of the app has the purpose of collecting information about the utilisation of a vacuum cleaner
# with the interaction of a game. This app will play a game and, in the same time, it will
# save information about he usage of the vacuum cleaner.
# There are 6 levels in the game, each one with a foe. Moving the vacuum cleaner generates
# hit points that weak the enemy. When enemy's HPs turn zero, the player move to the next level
# Special movements generate combo hits with extra damage
# The purpose of this app is to test it with users and try to understand if the vacuum cleaning behaviour
# change compared to the control app
# Each 30 seconds of usage will be saved as one 'token'. Other saved data are: time and kind of movement of the 
# vacuum cleaner on axes x and y (left/right up/down).
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
mov_before = '-'
# set no 30s movement tokens
token = 0
#variables for RTC
addr = 0x68
buf = bytearray(7)

# game function
# set game variables beginning programme
level = 1
hp = 150

# set count for display
time_count = 0

# set buffer type of movement for combo recognition
combo_buffer = ''

# set count for explosion effect
expl_count = 0

# set HP for each enemy
lev_hp = {
    1 : 150,
    2 : 300,
    3 : 600,
    4 : 1200,
    5 : 2400,
    6 : 3200,
    }

# set special movements that add extra score
combos = {
    'udud': 10,
    'dudu': 10,
    'rlrl': 10,
    'lrlr': 10,
    'udlr': 50,
    'rudl': 50,
    'lrud': 50,
    'dlru': 50
    }


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
        result = 'r'
    elif readx < -sens :
        result = 'l'
    elif ready > sens :
        result = 'u'
    elif ready < -sens :
        result = 'd'
    else :
        result = '-'
    return result


# function that control display : images
def images_display(value) :
    if value == 0 :
        #clean the screen
        display.clear()
    elif value == 1 :
        # enemy 1: Priv Stain
        display.show(Image('00900:99999:90909:99999:09090'))
    elif value == 2 :
        # enemy 2: Lieut Dirt
        display.show(Image('09090:99999:90909:99999:09090'))
    elif value == 3 :
        #enemy 3 : Capt Mold
        display.show(Image('90909:99999:90909:99999:09090'))
    elif value == 4  :
        # enemy 4: Major Spot
        display.show(Image('00900:99999:90909:99999:90909'))
    elif value == 5  :
        # enemy 5: Colonel Mud
        display.show(Image('09090:99999:90909:99999:90909'))
    elif value == 6  :
        # enemy 6: General Dust
        display.show(Image('90909:99999:90909:99999:90909'))
    elif value == 7 :
        # explosion
        exp_frame_1 = Image('00000:00000:00900:00000:00000')
        exp_frame_2 = Image('00000:09990:09090:09990:00000')
        exp_frame_3 = Image('99999:90009:90009:90009:99999')
        explosion = [ exp_frame_1, exp_frame_2, exp_frame_3 ]
        display.show(explosion, delay=500)


# function that control display : text
def text_display(value) :
    if value == 0 :
        display.scroll('DUST*INVADERS')
    elif value == 1 :
        display.scroll('Level 1: Priv Stain')
    elif value == 2 :
        display.scroll('Level 2: Lieut Dirt')
    elif value == 3 :
        display.scroll('Level 3: Capt Mold')
    elif value == 4 :
        display.scroll('Level 4: Maj Spot')
    elif value == 5 :
        display.scroll('Level 5: Col Mud')
    elif value == 6 :
        display.scroll('Level 6: Gen Dust')
    elif value == 7 :
        display.scroll('YOU*WIN*YOU*WIN*YOU*WIN*YOU*WIN')


# function identify combo 
def rate_score(buffer_mov) :
    # identify is set 4 movs = one of combos and report combo's score, otherwise report basic score
    score = lev_hp.get(buffer_mov, 4)
    if score != 4 :
        display.scroll('COMBO!')
        #go back to enemy 
        images_display(level)
    return score


# simple function that track 10 mins of use (20 tokens), then show name game and level
def display_info() :
    # increase time buffer
    time_count += 1
    if time_count > 20 :
        # show title game
        text_display(0)
        # show lev and enemy name
        text_display(level)
        images_display(level)
        # time buffer
        time_count = 0

       
# function to show animation explosion after 10 movement (included '-')          
def display_expl() :
    # increase explosion
    expl_count += 1
    if expl_count > 10 :
        # show explosion effect
        images_display(7)
        #go back to enemy 
        images_display(level)
        # reset explosion count
        expl_count = 0
        
# function that make the game advance (core of game's rules)
def attack(move) :
    # firstly remove '-' moves
    if move != '-' :
        # stack kind of attack
        if len(combo_buffer) < 4 :
            combo_buffer += str(move)
            print('loanding string: ' + str(combo_buffer) ) #print to check, remove from final vers
        elif len(combo_buffer) == 4 :
            #check kind of combo get combo's score, otherwise 4 hp
            attack = combos.get(combo_buffer, 4)
            print('attack remove ' + str(attack) + ' hp') #print to check, remove from final vers
            # upload hp enemy
            hp -= attack
            print ('enemy hp is now: ' + str(hp) ) #print to check, remove from final vers
        else : # string  > 4 chars
            print('ERROR string > 4 chars') #it should not happen

# function that check hp and move to next level/ reset game
# best but it into 30s cicle, otherwise to save battery but outside 30 sec cicle
def check_hp() :
    if hp <= 0 :
        if level < 6 :
            level += 1
            hp = lev_hp.get(level)
            # show new lev and enemy 
            text_display(level)
            images_display(level)
        elif level >= 6 : #reset game
            level = 1
            hp = lev_hp.get(level)
            text_display(7) # victory message
            # show new lev and enemy 
            text_display(level)
            images_display(level)

# write function cicle of 30 sec that save all new movements
def capture_30s(sens) :
    # show lev and enemy name if long time don't see
    display_info()
    # show enemy
    images_display(level)
    # initialise variables
    time_sec = 0
    right_n = 0
    left_n = 0
    up_n = 0
    down_n = 0
    mov_before_cicle = '-'
    # set 30s acquisition data cicle
    while time_sec <= 30 :
        # get movement
        mov_into_cicle = is_moving(sens)
        # set inner if cicle to be sure to save only changes
        if mov_into_cicle != mov_before_cicle :
            mov_before_cicle = mov_into_cicle
            print('in  cicle '+ str(mov_into_cicle)) # just to check, remove from final
            if mov_into_cicle == 'r' :
                right_n = right_n + 1
            elif mov_into_cicle == 'l' :
                left_n = left_n + 1
            elif mov_into_cicle == 'u' :
                up_n = up_n + 1
            elif mov_into_cicle == 'd' :
                down_n = down_n + 1
            # GAME FUNCTION HERE
            # stack 4 moves, give a score and reduce hp enemy
            attack(mov_into_cicle)
            # if hp enemy <= 0, upload enemy and score
            check_hp()
        sleep(500) # wait 0.5 sec before next reading
        time_sec = time_sec + 0.5 # advance time count   
    # after 30s out of cicle, return data as arrey of int
    display.clear() #turn off the led after 30 sec
    return [right_n, left_n, up_n, down_n]

# function to storage data in txt file    
def save_data(time2save, token2save, r2save, l2save, u2save, d2save) :
    # get string time in format YYYY-MM-DD HH:MM:SS
    time2save_string = str(time2save[3]) + '-' + str(time2save[4]) + '-' + str(time2save[5]) + '\t' + str(time2save[0]) + ':' + str(time2save[1]) + ':' + str(time2save[2]) + '\t' + str(time2save[6])
    #create string to save
    string2save = time2save_string + '\t' + str(token2save) + '\t' + str(r2save) + '\t' + str(l2save) + '\t' + str(u2save) + '\t' + str(d2save) + '\n'
    try :  # try to open existing file and copy data on saved_data
        with open('vacuum_data_game.txt', 'r') as my_file:
            saved_data = my_file.read()
    except OSError : # in case file do not exist create empty file and variable
        saved_data = '' 
        with open('vacuum_data_game.txt', 'w') as my_file:
            my_file.write('')
    #update data with new reading
    saved_data = saved_data + string2save
    print('saved data:') #just to chek, remove from final
    print(saved_data) #just to chek, remove from final
    #save new file with updated data
    with open('vacuum_data_game.txt', 'w') as my_file:
        my_file.write(saved_data)
    return


# start programme
# ===============================
 
while True :
    mov = is_moving(sensibility_sensor)
    if mov != mov_before :
        mov_before = mov
        token = token + 1 # token counter is updated
        print('identified movement! start cicle - ' + mov_before) # print to check remove from final
        data_30s = capture_30s(sensibility_sensor) #function 30s cicle + save movement
        print('token no: '+ str(token) + ', movements: R: ' + str(data_30s[0]) + ', L: ' + str(data_30s[1]) + ', U: ' + str(data_30s[2]) + ', D: ' + str(data_30s[3]) ) # print to check remove from final
        # read time
        time_now = get_time()
        #save data in file txt
        save_data(time_now, token, data_30s[0], data_30s[1], data_30s[2], data_30s[3]) 
    sleep(1000)