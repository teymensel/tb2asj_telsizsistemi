Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\TB2ASJ Telsiz.lnk")
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "c:\Users\blgsy\OneDrive\Documentos\tb2asj_telsizsistemi\baslat.bat"
oLink.WorkingDirectory = "c:\Users\blgsy\OneDrive\Documentos\tb2asj_telsizsistemi"
oLink.IconLocation = "shell32.dll,1"
oLink.Save
