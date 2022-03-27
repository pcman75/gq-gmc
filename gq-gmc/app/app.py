import json, yaml, threading, logging           # basic modules
import pathlib


# for GMC
import serial                                   # communication with serial port
import serial.tools.list_ports                  # allows listing of serial ports


from hassapi import triggerSensor

aoconfig = dict()
if(pathlib.Path('/data/options.json').is_file()):
    with open('/data/options.json') as f:
        aoconfig = json.load(f)
else:
    with open(pathlib.Path(__file__).parent.resolve()/'../config.yaml') as f:
        aoconfig = yaml.safe_load(f)["options"]
            
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging._nameToLevel[aoconfig["LogLevel"]])


def readCPM():
    try:
        with serial.Serial(aoconfig["GMCport"], aoconfig["GMCbaudrate"], timeout = aoconfig["GMCtimeout"]) as ser:
            bwrt = ser.write(b'<GETCPM>>')
            srec = ser.read(2)
            if len(srec) == 2:    
                value = srec[0] << 8 | srec[1]
                value = value & 0x3fff   # mask out high bits, as for CPS* calls on 300 series counters
                logger.info(f"CPM = {value}")
                triggerSensor("sensor.gmc_gq_cpm1", "Nuclear Radiation CPM 1", value, logger)
                triggerSensor("sensor.gmc_gq_usvh1", "Nuclear Radiation μSvh 1", value * 0.39/60, logger)
        
    except Exception as e:
        logger.error(e)  
            
    threading.Timer(aoconfig["UpdateInterval"], readCPM).start()
    
def main():
    readCPM()
    
if __name__ == '__main__':
    main()