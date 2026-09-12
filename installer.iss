; مُثبِّت Claude RTL — المسارات كلها نسبية لمكان الملف ده
[Setup]
AppName=Claude RTL
AppVersion=2.0
AppPublisher=Claude RTL
AppId={{E3A7F2D1-8B4C-4D5E-9F6A-1C2D3E4F5A6B}
DefaultDirName={autopf}\Claude RTL
UninstallDisplayName=Claude RTL
DefaultGroupName=Claude RTL
OutputDir=output
OutputBaseFilename=ClaudeRTL-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\ClaudeRTL.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic";  MessagesFile: "compiler:Languages\Arabic.isl"

[Files]
Source: "build\exe.win-amd64-*\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional options:"; Flags: unchecked
Name: "startup"; Description: "Start automatically when Windows starts"; GroupDescription: "Additional options:"

[Icons]
Name: "{group}\Claude RTL"; Filename: "{app}\ClaudeRTL.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall Claude RTL"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Claude RTL"; Filename: "{app}\ClaudeRTL.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ClaudeRTL"; ValueData: """{app}\ClaudeRTL.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\ClaudeRTL.exe"; Description: "Launch Claude RTL"; Flags: nowait postinstall skipifsilent
