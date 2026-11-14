from microbit import *
import radio

radio.config(channel=10, group=200)
radio.on()

while True:
    temp = temperature()
    light = display.read_light_level()

    direction = "none"
    if accelerometer.was_gesture('left'):
        direction = "left"
    elif accelerometer.was_gesture('right'):
        direction = "right"

    radio.send("temp=%d,light=%d,dir=%s" % (temp, light, direction))
    sleep(50)