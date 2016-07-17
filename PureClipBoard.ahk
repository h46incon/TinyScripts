; Remove the text format in clipboard

cb := ""
cb := Clipboard
if (cb = "") {
	MsgBox, No text data in clipboard
} else {
	Clipboard := cb
}

exit
