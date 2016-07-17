@echo off

set NTP_SERVERS="1.cn.pool.ntp.org"

@echo ------ Restart w32tm service...
net stop w32time
w32tm /unregister
w32tm /register
net start w32time

@echo ------ Update time...
w32tm /config /update /manualpeerlist:%NTP_SERVERS%
w32tm /resync

ping 127.1 -n 4 > NUL
