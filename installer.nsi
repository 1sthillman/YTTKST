; YouTube Mezat Yardımcısı - NSIS Kurulum Betiği
; NSIS 3.x ile çalışır - http://nsis.sourceforge.net/

; Temel tanımlamalar
!define APPNAME "YouTube Mezat Yardımcısı"
!define COMPANYNAME "YouTube Mezat Yardımcısı"
!define DESCRIPTION "YouTube canlı yayınları için mezat yardımcısı"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define ABOUTURL "https://www.example.com"

; Kurulum ayarları
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation"
RequestExecutionLevel admin

; Modern UI ayarları
!include "MUI2.nsh"
!define MUI_ICON "LOGO.png"
!define MUI_UNICON "LOGO.png"

; Modern UI sayfaları
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Dil dosyası
!insertmacro MUI_LANGUAGE "Turkish"

; Kurulum başlığı ve açıklaması
Name "${APPNAME}"
OutFile "YouTube_Mezat_Yardimcisi_Setup.exe"

; Kurulum bölümü
Section "!Ana Dosyalar" SecCore
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Ana uygulama dosyasını kopyala
  File "YouTube Mezat Yardimcisi.exe"
  File "LOGO.png"
  File "LICENSE.txt"
  File "license_codes.json"
  File "settings.json"
  
  ; Kullanıcı verileri varsa kopyala
  IfFileExists "auth_data.json" 0 +2
    File "auth_data.json"
  IfFileExists "license_usage.json" 0 +2
    File "license_usage.json"
  IfFileExists "paid_users.json" 0 +2
    File "paid_users.json"
  
  ; Masaüstü kısayolları
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\YouTube Mezat Yardimcisi.exe"
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\YouTube Mezat Yardimcisi.exe"
  
  ; Kaldırma bilgisi
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Kaldırma programını kaydet
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\YouTube Mezat Yardimcisi.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
SectionEnd

; Kaldırma bölümü
Section "Uninstall"
  ; Program dosyalarını kaldır
  Delete "$INSTDIR\YouTube Mezat Yardimcisi.exe"
  Delete "$INSTDIR\LOGO.png"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\license_codes.json"
  Delete "$INSTDIR\settings.json"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Kullanıcı verilerini kaldır - dikkatli olun!
  MessageBox MB_YESNO|MB_ICONQUESTION "Kullanıcı verilerini de silmek istiyor musunuz? (auth_data.json, license_usage.json, paid_users.json)" IDNO SkipUserData
    Delete "$INSTDIR\auth_data.json"
    Delete "$INSTDIR\license_usage.json"
    Delete "$INSTDIR\paid_users.json"
    Delete "$INSTDIR\mezat.log"
  SkipUserData:
  
  ; Klasörleri kaldır
  RMDir "$INSTDIR"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  ; Kısayolları kaldır
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  
  ; Registry kayıtlarını temizle
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
