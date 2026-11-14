from microbit import *
import radio

radio.config(channel=10, group=200)
radio.on()
THRESHOLD = 300

while True:
    temp = temperature()
    light = display.read_light_level()

    x = accelerometer.get_x()
    if x < -THRESHOLD:
        direction = "left"
    elif x > THRESHOLD:
        direction = "right"
    else:
        direction = "none"

    radio.send("temp=%d,light=%d,dir=%s" % (temp, light, direction))
    sleep(50)