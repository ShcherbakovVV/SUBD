Unicode true
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "MUI2.nsh"
!include "ReplaceInFile.nsh"
!define APPNAME "Торги фьючерсами"
!define DESCRIPTION "Установщик приложения для работы с базой данных торгов фьючерсами"
BrandingText " "
RequestExecutionLevel admin 

Name "${APPNAME}"
InstallDir "$PROGRAMFILES\${APPNAME}"
OutFile "futures-contracts-installer.exe"

!define MUI_WELCOMEPAGE_TITLE_3LINES "Вас приветствует мастер установки приложения Торги фьючерсами"
!define MUI_FINISHPAGE_TEXT "Установка завершена. $\n$\nПосле выхода из мастера установки приложение будет настроено. $\n$\n\
                             Не закрывайте окно настройки и следуйте инструкциям на экране."
 
!define MUI_PAGE_CUSTOMFUNCTION_SHOW WelcomeLabelLinks 
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH 

!define MUI_PAGE_CUSTOMFUNCTION_SHOW un.WelcomeLabel
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

Function WelcomeLabelLinks 
	${NSD_CreateLink} 120u 105u 100% 12u "https://dev.mysql.com/downloads/installer/"
	Pop $0
	SetCtlColors $0 0x0645AD transparent
	${NSD_OnClick} $0 onClickLink1
	${NSD_CreateLink} 120u 117u 100% 14u "https://www.python.org/downloads/"
	Pop $1
	SetCtlColors $1 0x0645AD transparent
	${NSD_OnClick} $1 onClickLink2
	${NSD_CreateLabel} 120u 50u 65% 72u "Чтобы начать установку, нажмите Далее.$\n$\n\
                                         ВНИМАНИЕ!!! Для работы приложения требуются установленные MySQL Server 8.0 и Python 3.9.0. $\n$\n\
							             Вы можете скачать их здесь:"
	Pop $2									 
	SetCtlColors $2 0x000000 transparent
FunctionEnd

Function un.WelcomeLabel 
	${NSD_CreateLabel} 120u 50u 65% 24u "Чтобы удалить приложение Торги фьючерсами, нажмите Далее."
	Pop $2									 
	SetCtlColors $2 0x000000 transparent
FunctionEnd

Function onClickLink1
	ExecShell "open" "https://dev.mysql.com/downloads/installer/"
FunctionEnd

Function onClickLink2
	ExecShell "open" "https://www.python.org/downloads/"
FunctionEnd

Function .onInstSuccess
	!insertmacro _ReplaceInFile "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" "secure-file-priv = " "#"
	!insertmacro _ReplaceInFile "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" "tmpdir = " "#"
	FileOpen $4 "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" a
	FileSeek $4 0 END
	FileWrite $4 "$\r$\n" ; we write a new line
	FileWrite $4 "tmpdir = $\"C:/temp/$\""
	FileWrite $4 "$\r$\n" ; we write a new line
	FileWrite $4 "secure-file-priv = $\"$\""
	FileClose $4 ; and close the file
    Exec conf.bat 
FunctionEnd

Function .onGUIEnd
	Linker::unload
FunctionEnd

Section "Install"
	SetOutPath "$INSTDIR\tkintertable"
	File /r "tkintertable\*"
	SetOutPath "$INSTDIR"
	File "main.py"
	File "tktbl.py"
	File "help.chm"
	File "fcb_db.sql"
	File "icon.ico"
	File "uninsticon.ico"
	File "start.bat"
	File "conf.bat"
	File "conf.py"
	CreateDirectory "C:\temp"
	WriteUninstaller "$INSTDIR\Uninstall.exe"
	CreateShortcut "$DESKTOP\Торги фьючерсами.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\icon.ico" 0
	CreateShortcut "$DESKTOP\Удалить Торги фьючерсами.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\uninsticon.ico" 0
SectionEnd

Section "Uninstall"
	RMDir /r "C:\temp"
	Delete "Uninstall.exe"
	Delete "$DESKTOP\Торги фьючерсами.lnk"
	Delete "$DESKTOP\Удалить Торги фьючерсами.lnk"
	RMDir /r $INSTDIR
SectionEnd

!insertmacro MUI_LANGUAGE "Russian"