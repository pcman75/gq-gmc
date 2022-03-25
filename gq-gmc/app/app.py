
import enum
import queue
import time, json, yaml              # basic modules
from os.path import exists
import pathlib


# for GMC
import serial                                   # communication with serial port
import serial.tools.list_ports                  # allows listing of serial ports



aoconfig = dict()

if(pathlib.Path('/data/options.json').is_file()):
    with open('/data/options.json') as f:
        aoconfig = json.load(f)
else:
    with open(pathlib.Path(__file__).parent.resolve()/'../config.yaml') as f:
        options = yaml.safe_load(f)["options"]
        for val in options:
            aoconfig.update(val)
            
def readGMC():
    
    cpmq = queue.Queue(60)
    cpm = 0
    
    for i in range(60):
        cpmq.put(0)  
    
    while True:
        try:
            # open the serial port with selected settings
            ser = serial.Serial(aoconfig["GMCport"], aoconfig["GMCbaudrate"], timeout = aoconfig["GMCtimeout"])
            
            while True:
                bwrt = ser.write(b'<HEARTBEAT1>>')  # send count per second data to host every second automatically
                
                srec = ser.read(2)    
                value = srec[0] << 8 | srec[1]
                value = value & 0x3fff   # mask out high bits, as for CPS* calls on 300 series counters
                cpm = cpm - cpmq.get() + value        
                cpmq.put(value)
                
                print('CPS = ', value, ' CPM = ', cpm, ' μSv/h = ', cpm*0.39/60)
                time.sleep(0.1)
        
        except Exception as e:
            time.sleep(1)
            print(e)  


readGMC()