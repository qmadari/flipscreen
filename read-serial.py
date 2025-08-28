import serial
import subprocess,json
from datetime import datetime

def getComPort(deviceName:str):
    powershellCmdPart1 = "PowerShell -Command \"& {Get-PnpDevice | " 
    powershellCmdPart2 = "Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | " 
    powershellCmdPart3 = "Where-Object {$_.FriendlyName -Like '*" + deviceName + "*'} | " 
    #powershellCmdPart4 = "Where-Object {$_.PNPDeviceID -Like '*PID_6015*'} | " 
    powershellCmdPart5 = "Select-Object FriendlyName | ConvertTo-Json}\""
    powershellCmd = powershellCmdPart1 + powershellCmdPart2 + powershellCmdPart3 + powershellCmdPart5
    # return subprocess.getoutput(powershellCmd)
    return json.loads(subprocess.getoutput(powershellCmd))['FriendlyName'].split('(')[-1].rstrip(')')


def capture():
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
            print(serialString.decode('ascii'))
        except:
            pass
    


if __name__ == "__main__":
    capture()


