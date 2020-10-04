import os, csv, mysql.connector, tkinter.font
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *

#функция, загружающая таблицу при старте и при применении фильтра
def load_and_filter(root, l_date, r_date, name, l_quot, r_quot):
    #удаление файла с таблицей, если он существует
    if os.path.exists('C:\\temp\\out.csv'):
        os.remove('C:\\temp\\out.csv')
    
    #соединение с базой данных
    #вместо 0000 указать свой пароль, указанный при установке MySQl
    #также необходимо удалить все после = в строке, начинающейся на "secure-file-priv"
    #(должно остаться просто secure-file-priv = )
    #в файле C:\ProgramData\MySQL\MySQL Server 8.0\my.ini (от имени администратора)
    #в тот же файл добавить строку tmpdir = "C:/temp/" и создать на диске C папку temp
    db = mysql.connector.connect( host='localhost',
                                  database='fut_cen_bum',
                                  user='root',
                                  password='0000' )        #добавить считывание из конфига и редактирование этих файлов
    dbcursor = db.cursor()
    dbcursor.callproc( 'filtr', (l_date, r_date, name, l_quot, r_quot) )
    dbcursor.close()
    db.close()

    #открытие файла с таблицей
    with open( 'C:\\temp\\out.csv', 'r' ) as tablefile:
        table = csv.DictReader( tablefile, fieldnames=('Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена',
                                                       'Мин.цена', 'Макс.цена', 'Число прод.') )
        table_format = ''
        row_id=0
        for row in table:
            row_id=row_id+1
            table_format = table_format + '{:>4}'.format(row_id) + ' │' + '{: <12}'.format(row['Дата торг.']+' │') \
                         + '{: <12}'.format(row['Код фьюч.']) + ' │' + '{: <12}'.format(row['Дата погаш.']+' │') \
                         + '{: <9}'.format(row['Тек.цена']) + '│' + '{: <9}'.format(row['Мин.цена']) +'│' \
                         + '{: <11}'.format(row['Макс.цена']) + '│' + '{: <11}'.format(row['Число прод.']) + '\n'
    #отображение таблицы
    table_out = ScrolledText( root, width=88, height=25, font=('Courier New', 9, 'underline italic bold') )
    table_out.insert( 0.1, table_format )
    table_out.place( x=10, y=30 )
    table_out.configure(state='disabled')

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
                else: pass
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
    #добавить проверку на существование еще одного окна
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
