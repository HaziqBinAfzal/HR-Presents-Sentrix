#ifndef SourceExe
  #define SourceExe "..\dist\windows\Sentrix.exe"
#endif
#ifndef OutputDir
  #define OutputDir "..\dist\windows"
#endif

#define AppName "Sentrix"
#define AppVersion "1.0.0"
#define AppPublisher "HR-Presents"
#define AppExeName "Sentrix.exe"

[Setup]
AppId={{A3B4557D-6811-4E35-8BAE-817E518860C1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Sentrix
DefaultGroupName=Sentrix
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=Sentrix-v1-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Sentrix"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Sentrix"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Sentrix"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\Sentrix\logs"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
