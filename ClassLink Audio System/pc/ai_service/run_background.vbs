Set WshShell = CreateObject("WScript.Shell")
' Run start.bat in hidden mode (0), and don't wait for completion (False)
WshShell.Run "cmd.exe /c start.bat", 0, False
