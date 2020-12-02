@echo off > nul         
rem отключение отображения ввода команд                                    
chcp 65001 > nul       
rem изменение кодировки                          
echo ----------------------------------------------------------------------------------
echo ---------------------------- Производится настройка... ---------------------------
echo ----------------------------------------------------------------------------------
echo Устанавливаются библиотеки...
pip -q --no-color --disable-pip-version-check install mysql-connector-python > nul
pip -q --no-color --disable-pip-version-check install scipy > nul
pip -q --no-color --disable-pip-version-check install tkcalendar > nul
pip -q --no-color --disable-pip-version-check install tkintertable > nul
rem получаем путь к папке с питоном, чтобы скопировать скорректированные библиотеки
set copycmd=/y 
where python > py.txt 
set /p pypath=< py.txt
set pp=%pypath:~0,-10%
copy tkintertable\Dialogs.py %pp%Lib\site-packages\tkintertable\Dialogs.py > nul
copy tkintertable\Tables.py %pp%Lib\site-packages\tkintertable\Tables.py > nul
del py.txt > nul
echo Библиотеки успешно установлены!
echo Устанавливается база данных...
if not exist "C:\temp\" mkdir C:\temp
:enter_login_pass
    set /p login=Введите логин от сервера MySQL: 
    set /p pass=Введите пароль от сервера MySQL: 
    set PATH=%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin; > nul 
    mysql --user="%login%" --password="%pass%" < fcb_db.sql > nul
if ERRORLEVEL 1 (echo Неправильный логин или пароль! 
                 goto :enter_login_pass)
echo База данных успешно установлена!
echo ----------------------------------------------------------------------------------
echo ------------------------------ Настройка завершена! ------------------------------
echo ----------------------------------------------------------------------------------
pause
