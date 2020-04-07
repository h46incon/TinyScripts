@ECHO OFF
SET ADB_EXEC=D:\DevTools\android_platform_tools\adb.exe
SET R6_DEVICE=A0445263


:LOOP_BEG

:: check every 60s
TITLE=R6W ...
timeout /T 60

%ADB_EXEC% devices | findstr /B "%R6_DEVICE%"
IF %ErrorLevel% NEQ 0 (
	GOTO LOOP_BEG
)
:: player is powered on
:: check 1 hours later
TITLE=R6W Wait ...
timeout /T 3600

%ADB_EXEC% devices | findstr /B "%R6_DEVICE%"
IF %ErrorLevel% NEQ 0 (
	GOTO LOOP_BEG
)

:: player still powered on, pause music to notify user
TITLE=R6W Pause ...
choice /C YN /D Y /T 60 /M "Pause music"
IF %ErrorLevel% NEQ 1 (
	GOTO LOOP_BEGd
)
:: send play_and_pause key (QQMusic only handler this key)
%ADB_EXEC%  -s "%R6_DEVICE%" shell input keyevent 85

:: shutdown
TITLE=R6W Shutdown ...
choice /C YN /D Y /T 60 /M "Y to shutdown, N continue playing"
IF %ErrorLevel% EQU 1 (
	%ADB_EXEC%  -s "%R6_DEVICE%" shell reboot -p
) ELSE (
	%ADB_EXEC%  -s "%R6_DEVICE%" shell input keyevent 85
)


GOTO LOOP_BEG