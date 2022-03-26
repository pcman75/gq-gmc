import json, yaml, threading            # basic modules
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
        aoconfig = yaml.safe_load(f)["options"]
            

def readCPM(ser):
    try:
        if not ser.isOpen():
            ser = serial.Serial(aoconfig["GMCport"], aoconfig["GMCbaudrate"], timeout = aoconfig["GMCtimeout"])
        
        bwrt = ser.write(b'<GETCPM>>')
        srec = ser.read(2)
        if len(srec) == 2:    
            value = srec[0] << 8 | srec[1]
            value = value & 0x3fff   # mask out high bits, as for CPS* calls on 300 series counters
            print('CPM = ', value)
        
    except Exception as e:
        ser.close()
        print(e)  
            
    threading.Timer(1, readCPM, [ser]).start()
    
def main():
    ser = serial.Serial()
    
    readCPM(ser) 
    
if __name__ == '__main__':
    main()