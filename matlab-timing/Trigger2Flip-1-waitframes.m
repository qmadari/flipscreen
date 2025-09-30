

sca;
close all;
clear;

delete(serialportfind);
[~,detectedb]=system('python C:\PROGS\detectbiosemiserial.py');
comport=['COM' (num2str(sscanf(detectedb,'COM%d')))];
baudrate=115200;
biosemitriggerinterface = serialport(comport,115200); % writing uint8 a = little endian byte 1 
%write(biosemitriggerinterface,'a',"uint8") 




PsychDefaultSetup(2);

screens = Screen('Screens');

screenNumber = max(screens);

% psychimaging init with grey
[window, windowRect] = PsychImaging('OpenWindow', screenNumber, WhiteIndex(screenNumber)/2);

topPriorityLevel = MaxPriority(window);

ifi = Screen('GetFlipInterval', window); % inter frame interval

%numSecs = 5; % test takes 5s
%numFrames = round(numSecs / ifi); 

numFrames = 30;

waitframes = 1; % flip every frame. 2 = flip every other frame


Priority(topPriorityLevel);
vbl = Screen('Flip', window);
for frame = 1:numFrames
    % waitframes variant

    % Black + pause 1s
    Screen('FillRect', window, [0 0 0]);
    Screen('DrawingFinished', window);
    vbl = Screen('Flip', window, vbl + (waitframes - 0.5) * ifi);
    pause(1)


    % Fill White + trigger + Flip + pause 0.25s
    Screen('FillRect', window, [1 1 1]);
    Screen('DrawingFinished', window);
    write(biosemitriggerinterface,'a',"uint8") 
    vbl = Screen('Flip', window, vbl + (waitframes - 0.5) * ifi);
    pause(0.25)
end
Priority(0);

sca;

