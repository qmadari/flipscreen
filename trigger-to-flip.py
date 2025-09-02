import serial
import subprocess,json
from datetime import datetime
import logging
import os, sys

def getComPort(deviceName:str):
    powershellCmdPart1 = "PowerShell -Command \"& {Get-PnpDevice | " 
    powershellCmdPart2 = "Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | " 
    powershellCmdPart3 = "Where-Object {$_.FriendlyName -Like '*" + deviceName + "*'} | " 
    #powershellCmdPart4 = "Where-Object {$_.PNPDeviceID -Like '*PID_6015*'} | " 
    powershellCmdPart5 = "Select-Object FriendlyName | ConvertTo-Json}\""
    powershellCmd = powershellCmdPart1 + powershellCmdPart2 + powershellCmdPart3 + powershellCmdPart5
    # return subprocess.getoutput(powershellCmd)
    return json.loads(subprocess.getoutput(powershellCmd))['FriendlyName'].split('(')[-1].rstrip(')')


def capture(logger):
    # Create the output file
        # current_datetime = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
        # file_name = current_datetime+".txt"
        # file = open(current_datetime, 'w')
        # print("File created : ", file_name)
        # file.close()
    # Find and start reading from the port

    print('capture started')
    serialPort = serial.Serial(
        port=getComPort("Silicon Labs"), baudrate=57600*2, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, parity='N'
    )
    serialString = ""  # Used to hold data coming over UART
    while 1:
        serialString =serialPort.readline()
        try:
            #print(serialString.decode('ascii'))
            devout = serialString.decode('ascii')
            trigger2flip = devout.split('#')[1].split(' ')[2]
            #logger.info(f"{serialString.decode('ascii')}")
            logger.info(f"{trigger2flip}")
        except:
            pass
    


if __name__ == "__main__":
    curdate = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    logfolder = f"{os.environ['userprofile']}\\Desktop\\"
    logfilenm = f"{curdate}.log"
    logpath = f"{logfolder}{logfilenm}"

    loglevel = logging.INFO
    logformat = f"%(asctime)s - %(message)s"
    stdout_handler = logging.StreamHandler(stream=sys.stdout) # Writes to terminal too, not just logfile
    file_handler = logging.FileHandler(filename=logpath)
    handlers = [file_handler, stdout_handler]


    logging.basicConfig(encoding='utf-8', level = loglevel, format=logformat, datefmt='%m/%d/%Y %I:%M:%S %p',handlers=handlers)
    
    logger = logging.getLogger('curdate')

    capture(logger)


