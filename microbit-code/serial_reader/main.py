from microbit import *

light = 1
temperature = 1

while True:
    if button_a.is_pressed():
        light = 1
        temperature = 1
    if button_b.is_pressed():
        light = 0
        temperature = 0
        
    print('{"light":', light, ',"temp":', temperature, '}')
    sleep(100)