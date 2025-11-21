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
##-- Import statements

import serial
from psychopy_gui_flipscreen_auto_trigger import FlipscreenAutoTriggerPsychopyGui
from psychopy_gui_flipscreen_auto_trigger import loggingConfig  #  optional 

# ... loggingConfig is optional, use if logging is desired and matches your use case ...
# ... optionally also import getComPort for simpler EEG interface detection ...

#-- Setup
# ... Create flipscreen auto trigger object with defautl values ...
flipscreen = FlipscreenAutoTriggerPsychopyGui()

# ... Complete customizable argument list ...
flipscreen = FlipscreenAutoTriggerPsychopyGui(flipScreenCom=None, eegCom=None, overrideTrig=None, openTrig=111, closeTrig=122, baud=115200, logger=None)

# ... Optional logger enabled variant ...
logger = loggingConfig() 
flipscreen = FlipscreenAutoTriggerPsychopyGui(logger=logger) 


#-- Phase 1: Manual triggers in your experiment script
eeg_port = serial.Serial('COM4', baudrate=115200) 
eeg_port.write(bytes([10]))  # Send trigger 10
eeg_port.flush()
# ... more manually sent triggers ...
eeg_port.close()  # IMPORTANT: When switching to Flipscreen auto-triggers, 
                  # close port before starting Flipscreen

#-- Phase 2: Automatic Flipscreen triggers
# ... startThread will connect to the EEG com port and send trig 111 ...
flipscreen.startThread() 
# ... show screen stimuli, Flipscreen sends triggers automatically ...

# Optional: Override both triggers to same value at any time
flipscreen.setOverrideTrigger(99)  # Both light and dark now send 99
# ... continue experiment ...
flipscreen.setOverrideTrigger(None)  # Back to normal (144 for light, 155 for dark)

# ... closeThread will close the connection to the EEG com port and send trig 122 ...
flipscreen.stopThread()  # Closes EEG serial port by itself

# ... Custom default trigger values can be set when creating the flipscreen object ...

#-- Phase 3: Back to experiment manual triggers
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
    
    def __init__(self, flipScreenCom=None, eegCom=None, overrideTrig=None, openTrig=111, closeTrig=122, baud=115200, logger=None):
        self.flipScreenCom = flipScreenCom if flipScreenCom else getComPort("Silicon Labs") # Autodetect Flipscreen
        self.eegCom = eegCom if eegCom else getComPort("Serial Port") # Autodetect EEG AD box
        self.baud = baud
        self.logger = logger
        self.running = False
        self.thread = None

        self.eegSerialPort = None
        
        # Trigger codes
        self.LIGHT_TRIGGER = 144
        self.DARK_TRIGGER = 155
        self.OVERRIDE_TRIGGER = overrideTrig
        self.OPEN_TRIGGER = openTrig
        self.CLOSE_TRIGGER = closeTrig
    
    def setOverrideTrigger(self,newOverrideTrig):
        self.OVERRIDE_TRIGGER = newOverrideTrig
        if self.logger:
            if newOverrideTrig is None:
                self.logger.info("Override disabled - reverting to normal triggers")
            else:
                self.logger.info(f"Override enabled - all triggers now: {newOverrideTrig}")
        else:
            if newOverrideTrig is None:
                print("Override disabled - reverting to normal triggers")
            else:
                print(f"Override enabled - all triggers now: {newOverrideTrig}")

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
            self.sendTrig(self.OPEN_TRIGGER)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to open EEG port {self.eegCom}: {e}")
            else:
                print(f"Failed to open EEG port {self.eegCom}: {e}")

    def closeEEGPort(self):
        if self.eegSerialPort and self.eegSerialPort.is_open:
            self.sendTrig(self.CLOSE_TRIGGER)
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

        # Local trigger values (can be overridden during runtime)
        lightTrig = self.LIGHT_TRIGGER
        darkTrig = self.DARK_TRIGGER
        override = False

        try:
            flipScreenSerialPort = serial.Serial(port=self.flipScreenCom, baudrate=self.baud, bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE, parity='N')
            
            if self.logger:
                self.logger.info(f"Connected to Flipscreen on {self.flipScreenCom}")
            else:
                print(f"Connected to Flipscreen on {self.flipScreenCom}")
            
            while self.running:
                try:
                    if self.OVERRIDE_TRIGGER and darkTrig != self.OVERRIDE_TRIGGER:
                        # override has just been enabled
                        override = True
                        lightTrig = self.OVERRIDE_TRIGGER
                        darkTrig = self.OVERRIDE_TRIGGER 
                    if (not self.OVERRIDE_TRIGGER) and override:
                        # override has just been disabled
                        override = False
                        lightTrig = self.LIGHT_TRIGGER
                        darkTrig = self.DARK_TRIGGER

                    serialString = flipScreenSerialPort.readline()
                    if not serialString:
                        continue

                    devout = serialString.decode('ascii').strip()
                    if '#t_light=' in devout:
                        self.sendTrig(lightTrig)
                        if self.logger:
                            self.logger.info(f"Flipscreen: {devout}")
                        else:
                            print(f"Flipscreen: {devout}")
                    
                    elif '#t_dark=' in devout:
                        self.sendTrig(darkTrig)
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
    logfilenm = f"FlipscreenAutoTrig_{curdate}.log"
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
    logger.info("[  Flipscreen Trigger Sender Thread Starting  ]")
    logger.info("[  For use with Psychopy GUI  ]")
    
    flipscreenTriggerSender = FlipscreenAutoTriggerPsychopyGui(logger=logger)
    flipscreenTriggerSender.startThread()
    
    logger.info("Thread running. Press Ctrl+C to stop.")
    
    try:
        ## Simulating experiment
        time.sleep(5)

        ## Override default light and dark triggers
        flipscreenTriggerSender.setOverrideTrigger(99)
        
        ## More experiment
        time.sleep(5)

        ## Restore normal light dark triggers, disable override
        flipscreenTriggerSender.setOverrideTrigger(None)

        ## Experiment sleeping forever
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[  Shutting down  ]")
        flipscreenTriggerSender.stopThread()
        logger.info("[  Flipscreen Trigger program stopped gracefully  ]")


if __name__ == "__main__":
    main()
