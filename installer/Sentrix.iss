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
UninstallDisplayIcon={app}\Sentrix.ico
SetupIconFile=payload\Sentrix.ico
SetupLogging=yes

[InstallDelete]
; Clean all previously installed application/runtime files before copying the
; new build. User data lives under %LOCALAPPDATA%\Sentrix and is deliberately
; not touched here.
Type: filesandordirs; Name: "{app}\Runtime"
Type: filesandordirs; Name: "{app}\Documentation"
Type: filesandordirs; Name: "{app}\instance"
Type: filesandordirs; Name: "{app}\uploads"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\templates"
Type: filesandordirs; Name: "{app}\static"
Type: files; Name: "{app}\Start Sentrix.bat"
Type: files; Name: "{app}\README.txt"
Type: files; Name: "{app}\Sentrix.exe"
Type: files; Name: "{app}\Sentrix.ico"

[Files]
Source: "payload\Runtime\*"; DestDir: "{app}\Runtime"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "payload\Start Sentrix.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "payload\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "payload\Sentrix.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Sentrix"; Filename: "{app}\Start Sentrix.bat"; WorkingDir: "{app}"; IconFilename: "{app}\Sentrix.ico"
Name: "{autodesktop}\Sentrix"; Filename: "{app}\Start Sentrix.bat"; WorkingDir: "{app}"; IconFilename: "{app}\Sentrix.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\Start Sentrix.bat"; Description: "Launch Sentrix"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; These are only legacy app-local folders under Program Files. Modern Sentrix
; stores writable customer data under %LOCALAPPDATA%\Sentrix, which uninstall
; intentionally preserves.
Type: filesandordirs; Name: "{app}\instance"
Type: filesandordirs; Name: "{app}\uploads"
Type: filesandordirs; Name: "{app}\logs"
