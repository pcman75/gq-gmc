import json, yaml, threading, logging, time           # basic modules
import pathlib
import queue


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

cpmq = queue.Queue(60)
for i in range(60):
    cpmq.put(0) 
cpm = 0
gmc_serial_number = 0

def readCPS():
    
    global cpm, cpmq, gmc_serial_number
    while True:
        try:
            with serial.Serial(aoconfig["GMCport"], aoconfig["GMCbaudrate"], timeout = aoconfig["GMCtimeout"]) as ser:
                
                bwrt = ser.write(b'<GETVER>>')
                srec = ser.read(14) # total 14 bytes ASCII chars from GQ GMC unit. It includes 7 bytes hardware model and 7 bytes firmware version.
                logger.info(f'GQ GMC Model: {srec.decode("UTF-8")}')
                
                bwrt = ser.write(b'<GETSERIAL>>')  # serial number in 7 bytes
                srec = ser.read(7)
                gmc_serial_number = int.from_bytes(srec, 'big')
                logger.info(f'GQ GMC Serial: {gmc_serial_number}')
                
                bwrt = ser.write(b'<HEARTBEAT1>>')  # send count per second data to host every second automatically
                while True:
                    srec = ser.read(2)    
                    value = srec[0] << 8 | srec[1]
                    value = value & 0x3fff   # mask out high bits, as for CPS* calls on 300 series counters
                    cpm = cpm - cpmq.get() + value        
                    cpmq.put(value)
                    
                    logger.debug(f'CPS = {value} CPM = {cpm} μSv/h = {cpm*0.39/60}')
                    
        except Exception as e:
            logger.error(e) 
            time.sleep(10)
          
def updateSensor():
    
    global cpm, gmc_serial_number
    
    try:
        logger.info(f'Nuclear radiation CPM = {cpm} μSv/h = {cpm*0.39/60}')
        triggerSensor("sensor.gmc_gq_cpm 2", "Nuclear Radiation CPM 2", gmc_serial_number, cpm, logger)
        triggerSensor("sensor.gmc_gq_usv 2", "Nuclear Radiation μSvh 2", gmc_serial_number, cpm * 0.39/60, logger)
    except Exception as e:
        logger.error(e)  
            
    threading.Timer(aoconfig["UpdateInterval"], updateSensor).start()
     
def main():
    threading.Timer(aoconfig["SensorWarmupTime"], updateSensor).start()
    readCPS()
    
if __name__ == '__main__':
    main()