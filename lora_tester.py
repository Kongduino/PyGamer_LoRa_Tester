import board, time, json, neopixel
from termio import cls as cls
from termio import printat as printat
from termio import rect as rect
from termio import fillrect as fillrect
f=''
u=''
c=''
# Button colors
RED = (255, 0, 0)
ORANGE = (255, 34, 0)
YELLOW = (255, 170, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
VIOLET = (153, 0, 255)
MAGENTA = (255, 0, 51)
PINK = (255, 51, 119)
AQUA = (85, 125, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)
NEO_BRIGHTNESS = 0.3
strip = neopixel.NeoPixel(board.NEOPIXEL, 5, brightness=NEO_BRIGHTNESS)
strip.fill(OFF)
time.sleep(0.5)

def blinkNeo(colour, times):
    global strip
    for i in range(0, times):
        strip.fill(colour)
        time.sleep(0.5)
        strip.fill(OFF)
        time.sleep(0.5)

def slideNeo():
    global strip
    strip.fill(OFF)
    strip[0]=(0,0,255)
    time.sleep(0.1)
    for i in range(1, 5):
        strip[i]=(0,0,255)
        for j in range(0, i-1):
            strip[j]=(0,0,255>>(i-j))
        time.sleep(0.1)
    while strip[4][2]>0:
        for j in range(0, 5):
            strip[j]=(0,0,strip[j][2]>>1)
        time.sleep(0.1)
    strip.fill(OFF)

def displayMessage():
    cls()
    printat(2, 2, "BastaGamer")
    printat(1,2,f"From {f}")
    printat(1,3,f"UUID {u}")
    printat(1,4,f"Msg  {c}")
    printat(1,5,f"SNR  {snr}")
    printat(1,6,f"RSSI  {rssi}")

def getElapsedTime(tm):
    if tm < 60:
        tm = int(tm)
        return f"{tm} s"
    if tm < 3600:
        mn = int(tm / 60)
        sc = int(tm - (mn * 60))
        return f"{mn} mn {sc} s"
    hr = int(tm / 3600)
    mn = int((tm - (hr * 3600))/60)
    sc = int(tm - (mn * 60) - (hr*3600))
    return f"{hr} hr {mn} mn {sc} s"

blinkNeo(RED, 3)
i2c = board.I2C()  # uses board.SCL and board.SDA
strLen = 0

cls()
# set cursor at x=5 and y=4 (from top left of screen) and write TEST
printat(2, 2, "BastaGamer")
rssi=0
snr = 0
lastCheck = time.monotonic()
lastPing = lastCheck
lastMessage = 0
strip.fill((0,0,0))

while True:
    tm = time.monotonic()
    if (tm-lastCheck)>10:
        #check with BastWan every 10 seconds
        cls()
        printat(2, 2, "BastaGamer")
        if lastMessage == 0:
            printat(1, 8,"No messages so far")
        else:
            elapsed = getElapsedTime(tm - lastMessage)
            displayMessage()
            printat(1, 8, f"Time elapsed: {elapsed}")
        #printat(1, 10,"try lock.......")
        while not i2c.try_lock():
            pass
        #printat(1, 10,"query count....")
        try:
            i2c.writeto(0x18, bytearray(b'/any'))
        except:
            #printat(1, 10,"error in any...")
            #blinkNeo(RED, 2)
            pass
        result = bytearray(3)
        result[0]=0
        try:
            i2c.readfrom_into(0x18, result)
        except:
            #printat(1, 10,"error in any2...")
            #blinkNeo(RED, 2)
            pass
        count = int(result[0])
        #print(f"Count: {count}")
        if count>0:
            slideNeo()
            lastMessage = time.monotonic()
            snr = int(result[1])-100
            rssi = int(result[2])*-1
            #printat(1, 8,"query message")
            msg = bytearray(count)
            i2c.writeto(0x18, bytearray(b'/msg'))
            i2c.readfrom_into(0x18, msg)
            try:
                obj=json.loads(msg.decode())
                u=obj["UUID"]
                c=obj["cmd"]
                f=obj["from"]
                displayMessage()
                #blinkNeo(GREEN, 2)
            except:
                #blinkNeo(RED, 2)
                printat(1, 8,"JSON error")
                printat(1, 9, msg)
        #printat(1, 10,"unlock........")
        i2c.unlock()
        lastCheck = time.monotonic()
    if (tm-lastPing)>600000:
        # Send a ping every 60 seconds
        printat(1, 9, "PING!")
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto(0x18, bytearray(b'/ping'))
        except:
            #blinkNeo(RED, 2)
            #printat(1, 10,"error in ping")
            pass
        i2c.unlock()
        lastPing = time.monotonic()
