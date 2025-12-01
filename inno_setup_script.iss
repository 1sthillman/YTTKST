#define MyAppName "YouTube Mezat Yardımcısı"
#define MyAppVersion "2.0"
#define MyAppPublisher "Mezat Yazılım"
#define MyAppURL "https://mezatyazilim.com"
#define MyAppExeName "mezaxx.py"

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
OutputBaseFilename=YouTube_Mezat_Yardimcisi_Setup
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

[Icons]
; Kısayollar
Name: "{group}\{#MyAppName}"; Filename: "{app}\YouTube_Mezat_Yardimcisi.bat"
Name: "{group}\Kılavuz"; Filename: "{app}\KURULUM_KILAVUZU.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\YouTube_Mezat_Yardimcisi.bat"; Tasks: desktopicon

[Run]
; Python yükle
Filename: "{tmp}\python-3.10.11-amd64.exe"; Parameters: "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0"; StatusMsg: "Python yükleniyor..."; Check: NeedsPython; Flags: waituntilterminated
; Modülleri yükle
Filename: "{cmd}"; Parameters: "/c cd ""{app}"" && python auto_installer.py"; StatusMsg: "Gerekli modüller yükleniyor..."; Flags: waituntilterminated runhidden
; Başlatma scripti oluştur
Filename: "{cmd}"; Parameters: "/c echo @echo off > ""{app}\YouTube_Mezat_Yardimcisi.bat"" && echo cd /d ""{app}"" >> ""{app}\YouTube_Mezat_Yardimcisi.bat"" && echo python mezaxx.py >> ""{app}\YouTube_Mezat_Yardimcisi.bat"""; StatusMsg: "Başlatma scripti oluşturuluyor..."; Flags: waituntilterminated runhidden
; Kurulum sonrası programı çalıştır
Filename: "{app}\YouTube_Mezat_Yardimcisi.bat"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall nowait skipifsilent

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
           'Program, masaüstünüzdeki kısayol ile çalıştırılabilir.', mbInformation, MB_OK);
  end;
end;