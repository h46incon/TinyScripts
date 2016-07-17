@echo off
set VPN_NAME="MyVPN"
set VPN_USERNAME="h46incon"
set VPN_PASSWD="password"


if "%1"=="" goto DEFAULT
if /I "%1"=="-connect" goto CONNECT
if /I "%1"=="-disconnect" goto DISCONNECT
goto HELP

:HELP
echo %0
echo     -connect     : Á¬½ÓVPN
echo     -disconnect  : ¶Ï¿ªVPN
goto NUL>NUL 2>NUL

:DEFAULT
goto help

:CONNECT
rasdial %VPN_NAME% %VPN_USERNAME% %VPN_PASSWD%
goto END


:DISCONNECT
echo Disconnecting %VPN_NAME%...
rasdial %VPN_NAME% /Disconnect
goto END

:end
ping -n 4 127.1 >NUL
