# https://brainbehaviour.labs.vu.nl/docs#/Supplementary%20TO3%20Docs/OpenSesame-python-Triggers.md

# C:\PROGS\Miniconda3\envs\psychopy\python.exe
import serial
import subprocess,json

def getComPort(deviceName:str):
    powershellCmdPart1 = "PowerShell -Command \"& {Get-PnpDevice | " 
    powershellCmdPart2 = "Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | " 
    powershellCmdPart3 = "Where-Object {$_.FriendlyName -Like '*" + deviceName + "*'} | " 
    #powershellCmdPart4 = "Where-Object {$_.PNPDeviceID -Like '*PID_6015*'} | " 
    powershellCmdPart5 = "Select-Object FriendlyName | ConvertTo-Json}\""
    powershellCmd = powershellCmdPart1 + powershellCmdPart2 + powershellCmdPart3 + powershellCmdPart5
    # return subprocess.getoutput(powershellCmd)
    return json.loads(subprocess.getoutput(powershellCmd))['FriendlyName'].split('(')[-1].rstrip(')')


if __name__ == '__main__':
    io_eeg = serial.Serial(
    port=getComPort('USB Serial Port'),
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )

    io_eeg.close()
    io_eeg.open()

    triggerint = 1
    io_eeg.write(triggerint.to_bytes(1,'little'))
    io_eeg.close() # make sure you close the port, otherwise the next user gets an error. 