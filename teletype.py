# Created by James Graham
# October 29, 2014
# based of of the library by cogwheelcircuitworks:
# https://github.com/cogwheelcircuitworks/teletype-pi/blob/master/teletype.py

import time
import threading
import RPi.GPIO as gpio


PWR_PIN = 5         #Controls motor
DTA_PIN = 7         #controls data
data_freq = 45.45
data_period = 1/data_freq # period for one bit (seconds) should be 45.5 Hz?

CurrColumnPos = 1
MaxColumnPos = 28   #how many characters fit on a line
Shifted = 0         # 0 = LTRS, 1 = FIGS

MtrTimerVal = 1 # seconds for motor to stay on after last character
MtrTimerCtr = 0 # counts down for motor
MtrTimerThread = None # motor timer taken care of on a separate thread
MtrStartTime = 0.5   # time to let motor get up to speed (seconds)

def motortimer():
    #Runs a thread  in the background to shut of the motor if timed out
    global MtrTimerCtr, MtrTimerVal, MtrTimerThread
    if (MtrTimerCtr):
        MtrTimerCtr = MtrTimerCtr -1
        if (not MtrTimerCtr):
            print 'Motor Timed Out'
            motorStop()
            print 'Data Pin Off'
            
        
    # restart thread if parent is still running
    for thread in threading.enumerate():
        if thread.getName().find("MainThread") != -1:
            if thread.is_alive() == True:
                MtrTimerThread = threading.Timer(1.0,motortimer)
                MtrTimerThread.start()
            else:
                print 'motortimer: Parent thread dead'

def start():
    gpio.setmode(gpio.BOARD)
    gpio.setup(PWR_PIN, gpio.OUT) # Setup GPIO pin 7 to OUT
    gpio.setup(DTA_PIN, gpio.OUT) # Setup GPIO pin 7 to OUT
    gpio.output(PWR_PIN, True)
    gpio.output(DTA_PIN,True)
    motortimer()

def motorStart():
    global MtrTimerCtr, MtrTimerVal
    if (not MtrTimerCtr):
        print 'Data Pin On'
        gpio.output(DTA_PIN, True)
        time.sleep(0.2)
        gpio.output(PWR_PIN, False)
        print "Motor start"
        time.sleep(MtrStartTime)
    MtrTimerCtr = MtrTimerVal

def motorStop():
    global MtrTimerCtr
    gpio.output(PWR_PIN, 1)
    gpio.output(DTA_PIN,False)
    MtrTimerCtr = 0
    
def shiftFigs():
    global Shifted
    if (not Shifted):
        Shifted = 1
        txctrl('figs')

def shiftLtrs():
    global Shifted
    if (Shifted):
        Shifted = 0
        txctrl('ltrs')

def columnPos():
    #tracks to position along to page and sends cr/lf 
    global CurrColumnPos, MaxColumnPos
    CurrColumnPos = CurrColumnPos + 1
    if (CurrColumnPos > MaxColumnPos):
        #txctrl('lf') Removed untill carriage return is working
        txctrl('cr')
        CurrColumnPos = 1

def highBit(pin, period):
    # Sends a 1 to the teletype
    gpio.output(pin, True)
    time.sleep(period)
    #can leave high since that is the default state

def lowBit(pin,period):
    #Sends a 0 to teletype
    gpio.output(pin,False)
    time.sleep(period)
    #gpio.output(pin,True)
    #should be okay to keep low, given that this should only be called through txbin()
    
def bitOut(pin, period, State):
    if (State == '1'):
        highBit(pin, period)
    elif (State == '0'):
        lowBit(pin, period)

def txbin(c):    
    #Transmits a binary sequence to the teletype
    motorStart()
    bitOut(DTA_PIN, data_period,'0') # start bit
    for bit in c[::-1]:
        bitOut(DTA_PIN, data_period, bit) # [::-1] reverses the order
        #print bit
    # Stop bits
    # Possible to replace with data_period*1.42 ?
    bitOut(DTA_PIN, data_period*1.5, "1") 
    #bitOut(DTA_PIN, data_period, "1") 
    
def txchar(c):
    # sends an ascii Character
    if c in ascii_to_baudot:
        a = ascii_to_baudot[c]
        if a in baudot_to_bin:
            b = baudot_to_bin[a]
            if (a in needs_shift):
                shiftFigs()
            else:
                shiftLtrs()
            txbin(b)
            #print a,b
        else:
            txctrl('space')
    else :
        txctrl('space') # if character can't be mapped, print space
    columnPos()

def txstr(s):
    # Sends a string to the teletype
    for i in s:
        txchar(i) 

def txString(s):
    # Sends a string to the teletype
    txstr(s)
    
def txctrl(c):
    # Transmits control codes to the teletype
    global ColumnCurrentPosition
    if (c == 'cr'): #Carriage return
        txbin('01000')
        print 'cr'
        ColumnCurrentPosition = 0
    elif (c == 'lf'): #line feed
        txbin('00010')
        print 'lf'
    elif (c == 'figs'):
        txbin('11011')
        print 'figs'
    elif ( c== 'ltrs'):
        txbin('11111')
        print 'ltrs'
    elif ( c == 'space'):
        txbin('00100')
        print 'space'
        columnPos()
    elif ( c == 'null'):
        txbin('00000')
        print 'null'
     
#  Use dictionary to map ascii characters to the baudot Characters
ascii_to_baudot = {
                   'a':'A',
                   'b':'B',
                   'c':'C',
                   'd':'D',
                   'e':'E',
                   'f':'F',
                   'g':'G',
                   'h':'H',
                   'i':'I',
                   'j':'J',
                   'k':'K',
                   'l':'L',
                   'm':'M',
                   'n':'N',
                   'o':'O',
                   'p':'P',
                   'q':'Q',
                   'r':'R',
                   's':'X', # 's' does not work
                   't':'T',
                   'u':'U',
                   'v':'V',
                   'w':'W',
                   'x':'X',
                   'y':'Y',
                   'z':'Z',
                   'A':'A',
                   'B':'B',
                   'C':'C',
                   'D':'D',
                   'E':'E',
                   'F':'F',
                   'G':'G',
                   'H':'H',
                   'I':'I',
                   'J':'J',
                   'K':'K',
                   'L':'L',
                   'M':'M',
                   'N':'N',
                   'O':'O',
                   'P':'P',
                   'Q':'Q',
                   'R':'R',
                   'S':'X', # 's' does not work
                   'T':'T',
                   'U':'U',
                   'V':'V',
                   'W':'W',
                   'X':'X',
                   'Y':'Y',
                   'Z':'Z',
                   '1':'1',
                   '2':'2',
                   '3':'3',
                   '4':'4',
                   '5':'5',
                   '6':'6',
                   '7':'7',
                   '8':'8',
                   '9':'9',
                   '0':'0',
                   '-': '-',
                   '?': '?',
                   ':': ':',
                   '$': '$',
                   '!': '!',
                   '&': '&',
                   '#': '#',
                   '(': '(',
                   ')': '(',
                   '.': '.',
                   ',': ',',
                   '\'': '\'',
                   '/': '/',
                   '"': '"',
                   ' ': ' ',
                   "'" : '"'
                   }
# then we map this set to baudot binary
baudot_to_bin = {
                'A' : '00011',
                'B' : '11001',
                'C' : '01110',
                'D' : '01001',
                'E' : '00001',
                'F' : '01101',
                'G' : '11010',
                'H' : '10100',
                'I' : '00110',
                'J' : '01011',
                'K' : '01111',
                'L' : '10010',
                'M' : '11100',
                'N' : '01100',
                'O' : '11000',
                'P' : '10110',
                'Q' : '10111',
                'R' : '01010',
                'S' : '00101',
                'T' : '10000',
                'U' : '00111',
                'V' : '11110',
                'W' : '10011',
                'X' : '11101',
                'Y' : '10101',
                'Z' : '10001',
                '1' : '10111',
                '2' : '10011',
                '3' : '00001',
                '4' : '01011',
                '5' : '10000',
                '6' : '10101',
                '7' : '00111',
                '8' : '00110',
                '9' : '11000',
                '0' : '10110',
                '-' : '00011',
                '?' : '11001',
                ':' : '01110',
                '$' : '01001',
                '!' : '01001',
                '&' : '11010',
                '#' : '10100',
                '(' : '01111',
                ')' : '10010',
                '.' : '11100',
                ',' : '01100',
                '\'' : '01010',
                '/' : '11101',
                '"' : '11101',
                ' ' : '00100'
                }
#these characters need to be shifted into FIGS
needs_shift = (
                  '1',
                  '2',
                  '3',
                  '4',
                  '5',
                  '6',
                  '7',
                  '8',
                  '9',
                  '0',
                  '-',
                  '?',
                  ':',
                  '$',
                  '!',
                  '&',
                  '#',
                  '(',
                  ')',
                  '.',
                  ',',
                  '\'',
                  '/',
                  '"'
                  )

start()
while True:
    text = raw_input("Enter a string: ")   
    if (text == 'exit'):
        gpio.cleanup()
        break
    if (text == 'cr'): #Carriage return
        print 'cr'
        txbin('01000')
        time.sleep(2)
        ColumnCurrentPosition = 0
    elif (text == 'lf'): #line feed
        txbin('00010')
        print 'lf'
    elif (text == 'figs'):
        txbin('11011')
        print 'figs'
    elif (text == 'ltrs'):
        txbin('11111')
        print 'ltrs'
    elif ( text == 'space'):
        txbin('00100')
        print 'space'
        columnPos()
    elif ( text == 'null'):
        txbin('00000')
        print 'null'
    print 'Sending to teletype'
    txstr(text)

