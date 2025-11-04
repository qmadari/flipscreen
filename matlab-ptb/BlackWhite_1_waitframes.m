

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


Priority(topPriorityLevel);
vbl = Screen('Flip', window);
for frame = 1:numFrames

    Screen('FillRect', window, [0 0 0]);

    vbl = Screen('Flip', window, vbl + (waitframes - 0.5) * ifi);

    Screen('FillRect', window, [1 1 1]);

    vbl = Screen('Flip', window, vbl + (waitframes - 0.5) * ifi);
end
Priority(0);


sca;
