from microbit import *
import radio

radio.config(channel=10, group=200)
radio.on()

while True:
    temp = temperature()
    display.scroll(temp)
    radio.send(str(temp))
    sleep(10)
    
    light = display.read_light_level()
    display.scroll(light)
    radio.send(str(light))
    sleep(10)

    direction = ("none")
    if accelerometer.was_gesture('left'):
        direction = "left"
    elif accelerometer.was_gesture('right'):
        direction = "right"
    display.scroll(direction)
    radio.send(direction)
    sleep(500)