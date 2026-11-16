Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\HP\Downloads\nexus\nexus_launcher.ps1""", 0, False
