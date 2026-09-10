; Inno Setup Script for TouchKey POS Pro
#define MyAppName "TouchKey POS Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TouchKey Software"
#define MyAppExeName "TouchKey_POS.exe"

[Setup]
AppId={{C8281B9A-5491-4D52-B981-98782E72D0FF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\TouchKey_POS
DisableProgramGroupPage=yes
OutputBaseFilename=TouchKey_POS_Setup
OutputDir=installer_output
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Запускать автоматически при включении Windows"; GroupDescription: "Параметры запуска:"

[Files]
Source: "dist\TouchKey_POS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить TouchKey POS Pro сейчас"; Flags: nowait postinstall skipifsilent
