import subprocess,json

print(json.loads(subprocess.getoutput("PowerShell -Command \"& {Get-PnpDevice | Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | Where-Object {$_.FriendlyName -Like '*USB Serial Port*'} | Where-Object {$_.PNPDeviceID -Like '*PID_6015*'} | Select-Object FriendlyName | ConvertTo-Json}\""))['FriendlyName'].split('(')[-1].rstrip(')'))

## Matlab
## [~,detectedb] = system('python C:\PROGS\detectbiosemiserial.py'); 
##comport = ['COM' (num2str(sscanf(detectedb,'COM%d')))] ;

## Python

#comport = subprocess.check_output('python C:\PROGS\detectbiosemiserial.py').strip().decode()
