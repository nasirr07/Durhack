from microbit import *
import radio 

radio.on()
radio.config(group=1)

while True:
    incoming = radio.receive()
    if incoming == "1":
        display.show(Image.HAPPY)
    else: 
        display.show(Image.SAD)
