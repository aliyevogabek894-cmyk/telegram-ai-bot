Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Teacher\Pictures\telegram AI"
WshShell.Run "pythonw.exe userbot.py", 0, False
