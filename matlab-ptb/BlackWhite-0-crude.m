

sca;
close all;
clear;

PsychDefaultSetup(2);

screens = Screen('Screens');

screenNumber = max(screens);

% psychimaging init with grey
[window, windowRect] = PsychImaging('OpenWindow', screenNumber, WhiteIndex(screenNumber)/2);

topPriorityLevel = MaxPriority(window);

ifi = Screen('GetFlipInterval', window); % inter frame interval

numSecs = 5; % test takes 5s
numFrames = round(numSecs / ifi); 

waitframes = 1; % flip every frame. 2 = flip every other frame

for frame = 1:numFrames

    Screen('FillRect', window, [0 0 0]);

    Screen('Flip', window);
    Screen('FillRect', window, [1 1 1]);

    Screen('Flip', window);
end 
sca;