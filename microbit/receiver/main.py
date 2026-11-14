from microbit import *
import radio 
import json 

radio.on()
radio.config(channel = 10, group = 200)

while True:
    incoming = radio.receive()
    if incoming is not None:
        print("Received data:", incoming)

        display.show(Image.RECEIVED)
        sleep(200)
        display.clear()

