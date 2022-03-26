import json, yaml, threading, logging            # basic modules
import pathlib


# for GMC
import serial                                   # communication with serial port
import serial.tools.list_ports                  # allows listing of serial ports

from hassapi import triggerSensor

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
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
            logger.info(f"CPM = {value}")
            #triggerSensor("gmc_gq_cpm", value, logger)
        
    except Exception as e:
        ser.close()
        logger.error(e)  
            
    threading.Timer(aoconfig["UpdateInterval"], readCPM, [ser]).start()
    
def main():
    readCPM(serial.Serial()) 
    
if __name__ == '__main__':
    main()