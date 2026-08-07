#define MyAppName "Sentrix"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "HR-Presents"
#define MyAppExeName "Sentrix.exe"

[Setup]
AppId={{7B2C53C6-07D7-4F5B-82DE-4A0D4183E776}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Sentrix
DefaultGroupName=Sentrix
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=Sentrix-Setup-v1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=Sentrix v1
SetupLogging=yes

[Files]
Source: "payload\Runtime\*"; DestDir: "{app}\Runtime"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "payload\Documentation\*"; DestDir: "{app}\Documentation"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "payload\Start Sentrix.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "payload\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Sentrix"; Filename: "{app}\Start Sentrix.bat"; WorkingDir: "{app}"
Name: "{autodesktop}\Sentrix"; Filename: "{app}\Start Sentrix.bat"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autoprograms}\Sentrix Documentation"; Filename: "{app}\Documentation"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\Start Sentrix.bat"; Description: "Launch Sentrix"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\instance"
Type: filesandordirs; Name: "{app}\uploads"
Type: filesandordirs; Name: "{app}\logs"
