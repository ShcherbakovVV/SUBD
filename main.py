import sys, os, csv, mysql.connector
from tkinter import *
from tkinter.ttk import *

#путь к этому скрипту
PATH = os.path.dirname(sys.argv[0])
#PATH.replace('\\\\', '\\')

#создание и настройка окна
root=Tk()                               
root.geometry('1000x400')               
root.title('Фьючерсы')

#соединение с базой данных
#вместо 0000 указать свой пароль, указанный при установке MySQl
#также необходимо удалить все после = в строке, начинающейся на "secure-file-priv"
#(должно остаться просто secure-file-priv = )
#в файле C:\ProgramData\MySQL\MySQL Server 8.0\my.ini (от имени администратора)
#в тот же файл добавить строку tmpdir = "C:/temp/" и создать на диске C папку temp
db = mysql.connector.connect( host='localhost',
                              database='fut_cen_bum',
                              user='root',
                              password='0000' )

#взаимодействие с MySQL - экспорт таблицы в csv
#if os.path.exists('C:\\temp\\out.csv'):
    #os.remove('C:\\temp\\out.csv')
cursor = db.cursor()
cursor.execute('USE fut_cen_bum;'
               #'SELECT \'Дата торг.\', \'Код фьюч.\', \'Дата погаш.\', \'Тек. цена\','
               #'\'Мин. цена\', \'Макс. цена\', \'Число прод.\' UNION ALL'
               'SELECT * FROM f_zb INTO OUTFILE \'C:/temp/out.csv\''
               ' FIELDS ENCLOSED BY \'"\' TERMINATED BY \';\'  ESCAPED BY \'"\';')

#открытие файла с таблицей
with open( 'C:\\temp\\out.csv' ) as tablefile:
    table = csv.reader( tablefile )

#НАДПИСИ
#надпись "Фильтры"
filters_label = Label( root, text='Фильтры', width=9 )
filters_label.place( x=674, y=30 )
#надпись "По дате торгов"
date_torg_label = Label( root, text='По дате торгов', width=14 )
date_torg_label.place( x=600, y=60 )
#надпись "ОТ (по дате)"
ot_date = Label( root, text='ОТ', width=3 )
ot_date.place( x=600, y=90 )
#надпись "ДО (по дате)"
do_date = Label( root, text='ДО', width=3 )
do_date.place( x=710, y=90 )
#надпись "По имени фьючерса"
name_label = Label( root, text='По имени фьючерса', width=20 )
name_label.place( x=600, y=120 )
#надпись "По котировке"
quot_label = Label( root, text='По котировке', width=17 )
quot_label.place( x=600, y=180 )
#надпись "ОТ (по котировке)"
ot_quot = Label( root, text='ОТ', width=3 )
ot_quot.place( x=600, y=210 )
#надпись "ДО (по котировке)"
do_quot = Label( root, text='ДО', width=3 )
do_quot.place( x=710, y=210 )

#текстовое поле для ввода левой границы даты
date_torg_from = Entry( root, width=13 )
date_torg_from.place( x=622, y=90 )
date_torg_from.insert(0, 'yyyy-mm-dd')           #поставить раннюю дату

#текстовое поле для ввода правой границы даты
date_torg_to = Entry( root, width=13 )
date_torg_to.place( x=733, y=90 )
date_torg_to.insert(0, 'yyyy-mm-dd')            #поставить самую позднюю дату

#список с выбором имени фьючерса
name_menu = Combobox( root )
name_menu['values'] = ('-Выберите фьючерс-', 'тест1', 'тест2', 'тест3')
name_menu.current(0)
name_menu.place( x=600, y=148 )

#текстовое поле для ввода левой границы котировки
quot_from = Entry( root, width=6 )
quot_from.place( x=622, y=210 )
quot_from.insert(0, '0')                        #поставить минимальное число

#текстовое поле для ввода правой границы котировки
quot_to = Entry( root, width=6 )
quot_to.place( x=732, y=210 )
quot_to.insert(0, '0')                          #поставить максимальное число

#проверка на правильность введенного формата данных
def date_check(date):
    if date=='': return False
    elif date[4]=='-' and date[7]=='-' and len(date)==10 and (date[:4]+date[5:7]+date[8:10]).isnumeric()==True and int(date[5:7])<=12:
        if date[5:7] in ('01','03','05','07','08','10','12'): #корректно ли число месяца для данных месяцев 
            if int(date[8:10])<=31: pass
            else: return False
        elif date[5:7] in ('04','06','09','11'):                
            if int(date[8:10])<=30: pass
            else: return False
        elif date[5:7]=='02':                                  
            if int(date[8:10])<=29: 
                if date[8:10]=='29': 
                    if ( int(date[:4])/4 ).is_integer()==True: pass       #проверка на високосный год
                    else: return False
                else: return False
            else: return False
        else: return False
    else: return False
    return True

#проверка quotation
def quot_check(quot):
    flag_dot = 0
    for symb in quot:                         #поиск недопустимых символов
        if symb.isnumeric()==True: pass
        elif symb=='.' or symb==',':
            flag_dot = flag_dot+1             #обнаружена одна запятая или точка, больше их уже быть не может
        elif flag_dot>1:                      #если найдена еще одна точка (такого быть не может)
            return False
        else: return False
    quot = quot.replace(',','.')
    if float(quot)<0:
        return False
    if quot[0]=='0' and quot[1]!='.' and len(quot)>1:          #если число начинается на 0, но не 0.
        return False
    return True

#функция, открывающая окно-уведомление об ошибке
def error_window(root, err_str):
    error_wnd = Toplevel(root)
    error_wnd.geometry('320x100+420+250')
    error_wnd.title('Ошибка')
    error_wnd.minsize(320,100)
    error_wnd.maxsize(320,100)
    error_msg = Label( error_wnd, text=err_str, anchor='center', width=40 )
    error_msg.place( relx=0.5, rely=0.33, anchor=CENTER )
    
    #кнопка ОК
    def error_ok_on(self):
        error_wnd.destroy()
    error_ok = Button( error_wnd, text='ОК', width=10 )
    error_ok.place( x=125, y=65 )
    error_ok.bind( '<Button-1>', error_ok_on )
    
    error_wnd.mainloop()

#кнопка "Применить фильтры"
def append_on(self):               #записывает введенные значения в переменные
    l_date = date_torg_from.get()
    r_date = date_torg_to.get()
    if date_check(l_date)==True and date_check(r_date)==True: 
        if int(l_date[:4])>int(r_date[:4]) or int(l_date[:4])==int(r_date[:4]) and int(l_date[5:7])>int(r_date[5:7]):
            error_window(root, 'Неправильно введена дата!')
        elif int(l_date[5:7])==int(r_date[5:7]) and int(l_date[8:10])>int(r_date[8:10]):   #разбито на 2 условия для удобства
            error_window(root, 'Неправильно введена дата!')
    else:
        error_window(root, 'Неправильно введена дата!')
        
    #доделать с выбором имени фьючерса
        
    l_quot = quot_from.get()
    r_quot = quot_to.get()
    if quot_check(l_quot)==False or quot_check(r_quot)==False:
        error_window(root, 'Неправильно введена котировка!')
    else:
        l_quot = l_quot.replace(',','.')
        r_quot = r_quot.replace(',','.')
        if float(l_quot)>float(r_quot):
            error_window(root, 'Неправильно введена котировка!')     
    
append = Button( root, text='Применить фильтры', width=22 )
append.place( x=628, y=270 )
append.bind( '<Button-1>', append_on )

#кнопка "Сбросить фильтры"
def clear_on(self):
    date_torg_from.delete(0, END)
    date_torg_from.insert(0, 'yyyy-mm-dd')      #поставить раннюю дату
    date_torg_to.delete(0, END)
    date_torg_to.insert(0, 'yyyy-mm-dd')        #поставить самую позднюю дату
    quot_from.delete(0, END)
    quot_from.insert(0, '0')                    #поставить минимальное число
    quot_to.delete(0, END)
    quot_to.insert(0, '0')                      #поставить максимальное число

clear = Button( root, text='Сбросить фильтры', width=22 )
clear.place( x=628, y=300 )
clear.bind( '<Button-1>', clear_on )

#отображение таблицы
#height = 5
#width = 5
#cells = {}
#for i in range(height):                        #строки
   # for j in range(width):                     #столбцы
    #    cell = Entry( root, text="", width=5 )
    #    cell.grid( row=i, column=j )
    #    cells[(i,j)] = cell
rows = 7
columns = 100
for i in range(rows):
    for j in range(columns):                     #столбцы
        cell = Entry( root, text="", width=9 )
        cell.place( x=20+59*i, y=30+21*j )
        
#tablescroll == Scrollbar( root, )

#кнопка "Новая запись"
newentry = Button( root, text='Новая запись', width=22 )
newentry.place( x=840, y=60 )

#кнопка "Удалить запись"
delentry = Button( root, text='Удалить запись', width=22 )
delentry.place( x=840, y=90 )

#кнопка "Редактировать запись"
editentry = Button( root, text='Редактировать запись', width=22 )
editentry.place( x=840, y=120 )

db.close()                   #закрытие соединения                    
root.mainloop()              #удержание окна
