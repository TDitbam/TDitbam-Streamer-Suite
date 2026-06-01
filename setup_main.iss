[Setup]
AppName=TDitbam Streamer Suite
AppVersion=3.1.0
DefaultDirName={autopf}\TDitbamStreamerSuite
DefaultGroupName=TDitbam Streamer Suite
OutputBaseFilename=TDitbam-StreamerSuite-v3.1.0-Setup
OutputDir=output
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\TDitbamStreamerSuite.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "optimizer_config.ini"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TDitbam Streamer Suite"; Filename: "{app}\TDitbamStreamerSuite.exe"
