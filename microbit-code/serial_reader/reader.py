import serial
from serial.tools.list_ports import comports 

# this microbit port vid = 3368
# this microbit port pid = 516

def FindMicrobitPort():
    for port in comports():
        if (port.vid == 3368) and (port.pid == 516):
            return port.device
    
    
microbit_port = FindMicrobitPort()
print(microbit_port)

with serial.Serial(microbit_port, 115200, timeout=1.0) as ser:
    ser.reset_input_buffer()
    while True:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="ignore").strip()
        if line:
            print("received:", line)