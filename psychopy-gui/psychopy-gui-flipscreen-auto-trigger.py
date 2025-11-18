import serial
import subprocess
import json
from datetime import datetime
import logging
import os
import sys
import threading
import time

"""
Flipscreen Automatic Trigger Sender for Psychopy GUI
 - Quinten Madari FGB-TO3 VU Amsterdam
 - Erik Claij FGB-TO3 VU Amsterdam

Brief usage comment:
--------------
# Import
from psychopy_gui_flipscreen_auto_trigger import FlipscreenAutoTriggerPsychopyGui, loggingConfig
import serial
# loggingConfig is optional, use if logging is desired and matches your use case
# optionally also import getComPort for simpler EEG interface detection.

# Setup
logger = loggingConfig() # optional
flipscreen = FlipscreenAutoTriggerPsychopyGui(logger=logger) 

# Phase 1: Manual triggers in your experiment script
eeg_port = serial.Serial('COM4', baudrate=115200) 
eeg_port.write(bytes([10]))  # Send trigger 10
eeg_port.flush()
# ... more manual triggers ...
eeg_port.close()  # IMPORTANT: When switching to Flipscreen auto-triggers, 
                  # close port before starting Flipscreen

# Phase 2: Automatic Flipscreen triggers
flipscreen.startThread() 
# ... show screen stimuli, Flipscreen sends triggers automatically ...
flipscreen.stopThread()  # Closes EEG serial port by itself

# Phase 3: Back to experiment manual triggers
eeg_port = serial.Serial('COM4', baudrate=115200) # Reopen EEG serial port for your main script
eeg_port.write(bytes([20]))  # Send trigger 20
eeg_port.close()
"""


def getComPort(deviceName: str):
    powershellCmdPart1 = "PowerShell -Command \"& {Get-PnpDevice | "
    powershellCmdPart2 = "Where-Object {$_.FriendlyName -Like '*(COM*'} | Where-Object {$_.Status -Like '*OK*'} | "
    powershellCmdPart3 = "Where-Object {$_.FriendlyName -Like '*" + deviceName + "*'} | "
    powershellCmdPart5 = "Select-Object FriendlyName | ConvertTo-Json}\""
    powershellCmd = powershellCmdPart1 + powershellCmdPart2 + powershellCmdPart3 + powershellCmdPart5
    return json.loads(subprocess.getoutput(powershellCmd))['FriendlyName'].split('(')[-1].rstrip(')')

## This is suitable for psychopy gui, serial used instead of pyserial. Other implementations likely will be with pyserial
class FlipscreenAutoTriggerPsychopyGui:
    
    def __init__(self, flipScreenCom=None, eegCom=None, baud=115200, logger=None):
        self.flipScreenCom = flipScreenCom if flipScreenCom else getComPort("Silicon Labs") # Autodetect Flipscreen
        self.eegCom = eegCom if eegCom else getComPort("Serial Port") # Autodetect EEG AD box
        self.baud = baud
        self.logger = logger
        self.running = False
        self.thread = None

        self.eegSerialPort = None
        
        # Trigger codes
        self.LIGHT_TRIGGER = 1
        self.DARK_TRIGGER = 2
    
    def startThread(self):
        self.running = True
        self.thread = threading.Thread(target=self._readFlipScreen, daemon=True)
        self.thread.start()
        if self.logger:
            self.logger.info(f"Flipscreen Trigger Sender started on {self.flipScreenCom}")
            self.logger.info(f"Trigger output on {self.eegCom}")
        else:
            print(f"Flipscreen Trigger Sender started on {self.flipScreenCom}")
            print(f"Trigger output on {self.eegCom}")
    
    def stopThread(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.logger:
            self.logger.info("Flipscreen Trigger Sender stopped")
        else:
            print("Flipscreen Trigger Sender stopped")
    
    def connectEEGPort(self):
        self.eegSerialPort = None
        try:
            self.eegSerialPort = serial.Serial(self.eegCom, baudrate=self.baud, timeout=0.01)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to open EEG port {self.eegCom}: {e}")
            else:
                print(f"Failed to open EEG port {self.eegCom}: {e}")

    def closeEEGPort(self):
        if self.eegSerialPort and self.eegSerialPort.is_open:
            self.eegSerialPort.close()

    def sendTrig(self,code):
        if self.eegSerialPort and self.eegSerialPort.is_open:
            try:
                self.eegSerialPort.write(bytes([code]))
                self.eegSerialPort.flush()
                if self.logger:
                    self.logger.info(f"TRIGGER_SENT: code={code}")
                else:
                    print(f"TRIGGER_SENT: code={code}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to send trigger {code}: {e}")
                else:
                    print(f"Failed to send trigger {code}: {e}")
        else:
            if self.logger:
                self.logger.error(f"EEG port not open, trigger {code} not sent")
            else:
                print(f"EEG port not open, trigger {code} not sent")

    def _readFlipScreen(self):
        flipScreenSerialPort = None
        self.connectEEGPort()
        try:
            flipScreenSerialPort = serial.Serial(port=self.flipScreenCom, baudrate=self.baud, bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE, parity='N')
            
            if self.logger:
                self.logger.info(f"Connected to Flipscreen on {self.flipScreenCom}")
            else:
                print(f"Connected to Flipscreen on {self.flipScreenCom}")
            
            while self.running:
                try:
                    serialString = flipScreenSerialPort.readline()
                    if not serialString:
                        continue

                    devout = serialString.decode('ascii').strip()
                    if '#light=' in devout:
                        self.sendTrig(self.LIGHT_TRIGGER)
                        if self.logger:
                            self.logger.info(f"Flipscreen: {devout}")
                        else:
                            print(f"Flipscreen: {devout}")
                    
                    elif '#dark=' in devout:
                        self.sendTrig(self.DARK_TRIGGER)
                        if self.logger:
                            self.logger.info(f"Flipscreen: {devout}")
                        else:
                            print(f"Flipscreen: {devout}")
                
                except UnicodeDecodeError:
                    pass
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error in readFlipScreen: {e}")
                    else:
                        print(f"Error in readFlipScreen: {e}")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to connect to Flipscreen: {e}")
            else:
                print(f"Failed to connect to Flipscreen: {e}")
        finally:
            self.closeEEGPort()
            if flipScreenSerialPort and flipScreenSerialPort.is_open:
                flipScreenSerialPort.close()


def loggingConfig():
    curdate = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    logfolder = f"{os.environ['userprofile']}\\Desktop\\"
    logfilenm = f"flipscreen_{curdate}.log"
    logpath = f"{logfolder}{logfilenm}"
    
    loglevel = logging.INFO
    logformat = "%(asctime)s - %(message)s"
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    file_handler = logging.FileHandler(filename=logpath)
    handlers = [file_handler, stdout_handler]
    
    logging.basicConfig(
        encoding='utf-8',
        level=loglevel,
        format=logformat,
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=handlers
    )
    
    logger = logging.getLogger('flipscreen')
    logger.info(f"Log file: {logpath}")
    return logger


def main():
    logger = loggingConfig()
    logger.info("[--Flipscreen Trigger Sender Thread Starting--]")
    logger.info("[--For use with Psychopy GUI--]")
    
    flipscreenTriggerSender = FlipscreenAutoTriggerPsychopyGui(logger=logger)
    flipscreenTriggerSender.startThread()
    
    logger.info("Thread running. Press Ctrl+C to stop.")
    
    try:
        ## Experiment sleeping forever
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[--Shutting down--]")
        flipscreenTriggerSender.stopThread()
        logger.info("[--Flipscreen Trigger program stopped cleanly--]")


if __name__ == "__main__":
    main()
