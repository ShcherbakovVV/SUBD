@echo off > nul
chcp 65001 > nul
echo ----------------------------------------------------------------------------------
echo ---------------------------- Производится настройка... ---------------------------
echo ----------------------------------------------------------------------------------
echo Устанавливаются библиотеки...
pip -q --no-color --disable-pip-version-check install mysql-connector-python > nul
pip -q --no-color --disable-pip-version-check install scipy > nul
pip -q --no-color --disable-pip-version-check install tkcalendar > nul
pip -q --no-color --disable-pip-version-check install tkintertable > nul
echo Библиотеки успешно установлены!
echo Устанавливается база данных...
:enter_login_pass
set /p login=Введите логин от сервера MySQL: 
set /p pass=Введите пароль от сервера MySQL: 
set PATH=%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin; > nul 
mysql --user="%login%" --password="%pass%" < fcb_db.sql > nul
if ERRORLEVEL 1 ( echo Неправильный логин или пароль! 
                  goto :enter_login_pass )
echo База данных успешно установлена!
echo ----------------------------------------------------------------------------------
echo ------------------------------ Настройка завершена! ------------------------------
echo ----------------------------------------------------------------------------------
pause
(Get-Content C:\ProgramData\MySQL\MySQL Server 8.0\my.ini) -replace 'secure-file-priv=', '#' | Out-File -encoding ASCII C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
echo secure-file-priv= >> C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
echo tmpdir = "C:/temp/" >> C:\ProgramData\MySQL\MySQL Server 8.0\my.ini

