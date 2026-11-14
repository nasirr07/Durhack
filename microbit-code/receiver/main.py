from microbit import *
import radio 

radio.on()
radio.config(channel = 10, group = 200)

while True:
    incoming = radio.receive()
    if incoming is not None:

        data = incoming.split(",")

        temp = int(data[0].split("=")[1])
        light = int(data[1].split("=")[1])
        direction = data[2].split("=")[1]

        print("Temperature:", temp)
        print("Light:", light)
        print("Direction:", direction)

    else:
        print("Invalid message:", incoming)
