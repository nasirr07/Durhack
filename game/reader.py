import serial, threading, json, time
from serial.tools.list_ports import comports

# this microbit port vid = 3368
# this microbit port pid = 516

class SerialReader():
    def __init__(self):
        self.microbit_port = self.FindMicrobitPort()
        self.data = {"temp": None, "light": None, "dir": None}
        self.do_read_serial = False

    def FindMicrobitPort(self):
        for port in comports():
            if (port.vid == 3368) and (port.pid == 516):
                return port.device
    
    def ReadSerial(self):
        if not self.microbit_port:
            return
        while self.do_read_serial:
            with serial.Serial(self.microbit_port, 115200, timeout=1.0) as ser:
                ser.reset_input_buffer()
                while self.do_read_serial:
                    raw = ser.readline()
                    if not raw:
                        continue
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if not (line.startswith("{") and line.endswith("}")):
                        continue
                    try:
                        line_data = json.loads(line)
                        for k, v in line_data.items():
                            self.data[k] = v
                    except json.JSONDecodeError:
                        continue
                    
    
    def Start(self):
        print("started")
        self.do_read_serial = True
        thread = threading.Thread(target=self.ReadSerial, daemon=True)
        thread.start()
        print("reading")
    
    def Stop(self):
        print("stopped")
        self.do_read_serial = False
                
    def GetSerialData(self):
        return self.data
