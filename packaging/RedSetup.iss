; RED Inno Setup Configuration Script
; This script mimics the pristine installation strategy of DynamicWin.

#define MyAppName "RED"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "The Obsidian Studios"
#define MyAppExeName "RED.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{D1A2B3C4-E5F6-4A5B-9C0D-E1F2A3B4C5D6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=C:\Users\Danny's PC\OneDrive\Documents\Personal Works\CODE\RED\RedCore\build
OutputBaseFilename=RedSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=C:\Users\Danny's PC\OneDrive\Documents\Personal Works\CODE\RED\RedCore\ui\red_logo.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Copy everything from the PyInstaller output directory (including the Electron UI inside)
Source: "C:\Users\Danny's PC\OneDrive\Documents\Personal Works\CODE\RED\RedCore\dist\RED_DIST\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu Shortcut
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Startup Folder Shortcut (Silent boot on Windows login)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Tasks]
Name: "autostart"; Description: "Start RED automatically when Windows boots"; GroupDescription: "Additional icons:"

[Run]
; Launch the app instantly after installation finishes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
