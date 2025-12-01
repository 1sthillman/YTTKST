#define MyAppName "YouTube Mezat Yardımcısı"
#define MyAppVersion "2.0"
#define MyAppPublisher "Mezat Yazılım"
#define MyAppURL "https://mezatyazilim.com"
#define MyAppExeName "YouTube_Mezat_Yardimcisi.bat"

[Setup]
; Kurulum ayarları
AppId={{3A8F2C61-F3B2-4D5A-9B8E-7D2D9F8A1E45}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Kurulum için yönetici hakları gerekli
PrivilegesRequired=admin
OutputDir=.
OutputBaseFilename=YouTube_Mezat_Yardimcisi_Setup_v2
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Windows 10 görünümü
WizardResizable=yes

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "Masaüstü kısayolu oluştur"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenuicon"; Description: "Başlat menüsü kısayolu oluştur"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Python yükleyicisi
Source: "python-3.10.11-amd64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedsPython
; Program dosyaları
Source: "mezaxx.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "auto_installer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "license_codes.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "LOGO.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "KURULUM_KILAVUZU.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "settings.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "sound\*"; DestDir: "{app}\sound"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\sound"; Permissions: users-modify

[Icons]
; Kısayollar
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Kılavuz"; Filename: "{app}\KURULUM_KILAVUZU.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Python yükle
Filename: "{tmp}\python-3.10.11-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"; StatusMsg: "Python yükleniyor..."; Check: NeedsPython; Flags: waituntilterminated
; Başlatma scripti oluştur
Filename: "{cmd}"; Parameters: "/c echo @echo off > ""{app}\{#MyAppExeName}"" && echo cd /d ""{app}"" >> ""{app}\{#MyAppExeName}"" && echo python -m pip install --upgrade pip >> ""{app}\{#MyAppExeName}"" && echo python -m pip install -r requirements.txt >> ""{app}\{#MyAppExeName}"" && echo python mezaxx.py >> ""{app}\{#MyAppExeName}"""; StatusMsg: "Başlatma scripti oluşturuluyor..."; Flags: waituntilterminated runhidden
; Başlatma scriptine yetki ver
Filename: "{cmd}"; Parameters: "/c attrib +x ""{app}\{#MyAppExeName}"""; Flags: waituntilterminated runhidden
; Kurulum sonrası programı çalıştır
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: files; Name: "{app}\{#MyAppExeName}"
Type: files; Name: "{app}\*.pyc"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
function NeedsPython: Boolean;
var
  ResultCode: Integer;
begin
  // Python kurulu mu kontrol et
  Result := True;
  if Exec(ExpandConstant('{cmd}'), '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Result := (ResultCode <> 0);
end;

// Kurulum başlangıcında hoş geldiniz mesajı
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'YouTube Mezat Yardımcısı''na Hoş Geldiniz!';
  WizardForm.WelcomeLabel2.Caption := 'Bu sihirbaz, YouTube Mezat Yardımcısı v2.0''ı bilgisayarınıza kuracak.' + #13#10 + #13#10 +
                                     'Kurulum, gerekirse Python''u otomatik olarak yükleyecek ve tüm bağımlılıkları kuracaktır.' + #13#10 + #13#10 +
                                     'Devam etmek için İleri butonuna tıklayın.';
end;

// Kurulum tamamlandığında bilgi mesajı
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('YouTube Mezat Yardımcısı başarıyla kuruldu!' + #13#10 + #13#10 +
           'Program şimdi başlatılacak. Sonraki kullanımlar için masaüstündeki kısayolu kullanabilirsiniz.', mbInformation, MB_OK);
  end;
end;

