import serial
import subprocess,json
from datetime import datetime
import logging
import os, sys

# stats
import numpy as np
import pandas as pd


def getComPort(deviceName:str):
    powershellCmdPart1 = "PowerShell -Command \"& {Get-PnpDevice | " 
    powershellCmdPart2 = "Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | " 
    powershellCmdPart3 = "Where-Object {$_.FriendlyName -Like '*" + deviceName + "*'} | " 
    #powershellCmdPart4 = "Where-Object {$_.PNPDeviceID -Like '*PID_6015*'} | " 
    powershellCmdPart5 = "Select-Object FriendlyName | ConvertTo-Json}\""
    powershellCmd = powershellCmdPart1 + powershellCmdPart2 + powershellCmdPart3 + powershellCmdPart5
    # return subprocess.getoutput(powershellCmd)
    return json.loads(subprocess.getoutput(powershellCmd))['FriendlyName'].split('(')[-1].rstrip(')')


def parse2record(parsedSerial):
    found = [str(item).replace(';','').split('=')[0] for item in parsedSerial]
    record = dict([(key,float(value)) for [key,value] in found])

    # searchstrings = ['rA2rA','rA2fA','fA2rA','fA2fA', #A
    #                  'rB2rB','rB2fB','fB2rB','fB2fB', #B
    #                  'rA2rB','rA2fB','fA2rB','fA2fB', #A -> B
    #                  't_dark','t_light',              #Light & dark labels
    #                 ]

    return record
    
def descriptives(a):
    
    pd.DataFrame(a)


def capture(logger, filterString = None):
    print('prepping data array')


    print('connecting to Flipscreen device')
    serialPort = serial.Serial(
        port=getComPort("Silicon Labs"), baudrate=57600*2, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, parity='N'
    )

    print('capture started')
    

    serialString = ""  # Used to hold data coming over UART
    while 1:
        serialString =serialPort.readline()
        try:
            devout = serialString.decode('ascii')
            parsedSerial = devout.split('#')[1].split(' ')
            record = parse2record(parsedSerial)
            

            if filterString:
                if filterString in record: logger.info(f'{filterString}: {record['filterString']}') 
            else:
                logger.info(devout)
        except:
            pass
    


if __name__ == "__main__":

    # Input argument handle
    farg = None
    if len(sys.argv) > 1:
        farg = str(sys.argv[1])
        print(f"Filterargument specified: {farg}")


    # Log
    # - Path and name
    curdate = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    logfolder = f"{os.environ['userprofile']}\\Desktop\\"
    logfilenm = f"{curdate}.log"
    logpath = f"{logfolder}{logfilenm}"

    # - Config
    loglevel = logging.INFO
    logformat = f"%(asctime)s - %(message)s"
    stdout_handler = logging.StreamHandler(stream=sys.stdout) # Writes to terminal too, not just logfile
    file_handler = logging.FileHandler(filename=logpath)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(encoding='utf-8', level = loglevel, format=logformat, datefmt='%m/%d/%Y %I:%M:%S %p', handlers=handlers)
    logger = logging.getLogger('curdate')


    # Start capture procedure
    capture(logger,farg)


