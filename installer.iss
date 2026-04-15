[Setup]
AppName=AnalyX
AppVersion=1.0.0
AppPublisher=AnalyX
AppPublisherURL=https://www.example.com
AppSupportURL=https://www.example.com
AppUpdatesURL=https://www.example.com
DefaultDirName={autopf}\AnalyX
DefaultGroupName=AnalyX
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=dist
OutputBaseFilename=AnalyX-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\AnalyX.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AnalyX"; Filename: "{app}\AnalyX.exe"
Name: "{commondesktop}\AnalyX"; Filename: "{app}\AnalyX.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AnalyX.exe"; Description: "启动 AnalyX"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
