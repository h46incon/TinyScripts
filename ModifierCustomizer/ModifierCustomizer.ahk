#NoEnv
SetBatchLines -1
ListLines Off
Process Priority,,High

SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force

; Set tray icon 
#NoTrayIcon
IconFileName := "Icon.ico"
Menu TRAY, Icon
IfExist %IconFileName%
  Menu TRAY, Icon, %IconFileName%

SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

ESC & H::Send {Left}
ESC & J::Send {Down}
ESC & K::Send {Up}
ESC & L::Send {Right}

ESC & C::Send ^{Insert}
ESC & V::Send +{Insert}

ESC::Send {Esc}
