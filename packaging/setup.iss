; Inno Setup Script for TDitbam Streamer Suite Pro
; Version: 3.1.0

[Setup]
AppId={{D17BA111-5555-4444-AA11-BB22CC33DD44}
AppName=TDitbam Streamer Suite Pro
AppVersion=3.1.0
AppPublisher=TDitbam & Gemini CLI
DefaultDirName={autopf}\TDitbamStreamerSuite
DefaultGroupName=TDitbam Streamer Suite Pro
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=TDitbam-StreamerSuite-v3.1.0-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "thai"; MessagesFile: "compiler:Languages\Thai.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\TDitbamStreamerSuite.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TDitbam Streamer Suite Pro"; Filename: "{app}\TDitbamStreamerSuite.exe"
Name: "{group}\{cm:UninstallProgram,TDitbam Streamer Suite Pro}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\TDitbam Streamer Suite Pro"; Filename: "{app}\TDitbamStreamerSuite.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TDitbamStreamerSuite.exe"; Description: "{cm:LaunchProgram,TDitbam Streamer Suite Pro}"; Flags: nowait postinstall skipifsilent
