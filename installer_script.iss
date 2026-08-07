#define MyAppName "TDitbam Streamer Suite"
#define MyAppVersion "3.6.0"
#define MyAppPublisher "Tditbam"
#define MyAppURL "https://github.com/TDitbam/TDitbam-Streamer-Suite"
#define MyAppExeName "StreamerSuite.exe"

[Setup]
AppId={{D3D3A6A0-9E1D-4F1B-9D8F-B9E3A5A0A1E0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
SetupIconFile=icon.ico
OutputDir=installer
OutputBaseFilename=TDitbam-Streamer-Suite-Setup-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
DiskSpanning=yes
DiskSliceSize=50000000
SlicesPerDisk=1
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\StreamerSuite\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{app}\logs"
Name: "{app}\msg_queue"
Name: "{app}\temp_audio"
