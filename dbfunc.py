import os, csv, mysql.connector
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *

#функция, делающая запрос по таблице
def load_and_filter(username, username_password, l_date, r_date,
                    name, l_quot, r_quot, ord_column, ord_ascdesc):
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
                                  user=username,
                                  password=username_password )    #добавить считывание из конфига и редактирование этих файлов
    dbcursor = db.cursor()
    dbcursor.callproc( 'filtr', (l_date, r_date, name, l_quot, r_quot, ord_column, ord_ascdesc) )
    dbcursor.close()
    db.close()

    with open( 'C:\\temp\\out.csv', 'r' ) as tablefile:
        table = csv.DictReader( tablefile, fieldnames=('Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена',
                                                       'Мин.цена', 'Макс.цена', 'Число прод.') )
        table_format = ''
        row_id = 0
        for row in table:
            row_id=row_id+1
            table_format = table_format + '{:>4}'.format(row_id) + ' │' + '{: <12}'.format(row['Дата торг.']+' │') \
                         + '{: <12}'.format(row['Код фьюч.']) + ' │' + '{: <12}'.format(row['Дата погаш.']+' │') \
                         + '{: <9}'.format(row['Тек.цена']) + '│' + '{: <9}'.format(row['Мин.цена']) +'│' \
                         + '{: <11}'.format(row['Макс.цена']) + '│' + '{: <11}'.format(row['Число прод.']) + '\n'
    return table_format

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

#проверка на хронологию дат(левая меньше правой)
def chrono_check(l_date, r_date):
    if ( date_check(l_date)==False or date_check(r_date)==False or  
         int(l_date[:4])>int(r_date[:4]) or int(l_date[:4])==int(r_date[:4]) and
         int(l_date[5:7])>int(r_date[5:7]) or int(l_date[5:7])==int(r_date[5:7]) and
         int(l_date[8:10])>int(r_date[8:10]) ):
        return False
    return True

#проверка quotation
def quot_check(quot):
    flag_dot = 0
    if quot=='': return False
    for symb in quot:                         #поиск недопустимых символов
        if symb.isnumeric()==True: pass
        elif symb=='.' or symb==',':
            flag_dot += 1                     #обнаружена одна запятая или точка, больше их уже быть не может
        elif flag_dot>1:                      #если найдена еще одна точка (такого быть не может)
            return False
        else: return False
    quot = quot.replace(',','.')
    if float(quot)<0: return False
    if quot[0]=='0' and quot[1]!='.' and len(quot)>1: return False  #если число начинается на 0, но не 0.
    return True

#проверка номера записи для удаления
def del_check(delete, max_entry):
    if delete=='': return False
    for symb in delete:                       #поиск недопустимых символов
        if symb.isnumeric()==False or symb=='':
            if symb==' ': pass
            else: return False
    del_list = [int(to_del) for to_del in delete.split(' ')]
    print(del_list)
    for dlist in del_list:
        if dlist<=0: return False
        if dlist>max_entry: return False
        if dlist==0: return False
    return True

#проверка номера записи для изменения
def edit_check(edit, max_entry):
    if edit=='': return False
    for symb in edit:                         #поиск недопустимых символов
        if symb.isnumeric()==False: return False
    if int(edit)<=0: return False
    if edit[0]=='0': return False             #если введено число, начинающееся 0.
    if int(edit)>max_entry: return False
    return True

#подсчет строк
def count_rows(text):
    row_num = text.count('\n')-1              #+1 пустая строка
    return row_num

#функция, открывающая окно с изменением/добавлением записи
def edit_new_window(root, edit_or_new_str):
    
    #добавить проверку на существование еще одного окна
    
    edit_new_wnd = Toplevel(root)
    edit_new_wnd.geometry('590x140+420+250')
    edit_new_wnd.title( edit_or_new_str )
    edit_new_wnd.minsize(590,140)
    edit_new_wnd.maxsize(590,140)
    edit_new_msg = Label( edit_new_wnd, text=edit_or_new_str, font=('TkDefault', 12, 'bold'), anchor='center', width=40 )
    edit_new_msg.place( relx=0.5, rely=0.1, anchor=CENTER )
    
    #отображение заголовков колонок таблицы
    table_header_en = Text( edit_new_wnd, width=80, height=1, font=('Courier New', 9, 'bold') )
    table_header_en.insert(0.1,' Дата торг.    Код фьюч.   Дата погаш. Тек.цена  Мин.цена  Макс.цена Число прод.')
    table_header_en.place( x=10, y=30 )
    table_header_en.configure(state='disabled')

    #ячейки для ввода
    torg_date_en = Entry( edit_new_wnd, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    torg_date_en.place( x=10, y=50 )
    name_en = Entry( edit_new_wnd, width=12, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    name_en.place( x=95, y=50 )
    day_end_en = Entry( edit_new_wnd, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    day_end_en.place( x=196, y=50 )
    quot_en = Entry( edit_new_wnd, width=8, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    quot_en.place( x=281, y=50 )
    min_quot_en = Entry( edit_new_wnd, width=8, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    min_quot_en.place( x=350, y=50 )
    max_quot_en = Entry( edit_new_wnd, width=8, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    max_quot_en.place( x=419, y=50 )
    num_contr_en = Entry( edit_new_wnd, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
    num_contr_en.place( x=488, y=50 )

    #пояснения к ячейкам
    date_format_torg = Label( edit_new_wnd, text='yyyy-mm-dd', font=('TkDefaultFont', 9), width=10 )
    date_format_torg.place( x=18, y=73 )
    date_format_end = Label( edit_new_wnd, text='yyyy-mm-dd', font=('TkDefaultFont', 9), width=10 )
    date_format_end.place( x=204, y=73 )
    name_format = Label( edit_new_wnd, text='12345-6789', font=('TkDefaultFont', 9), width=10 )
    name_format.place( x=110, y=73 )
    
    #кнопка "Применить"
    def edit_new_set_on(self):
        torg_date_entry = torg_date_en.get()
        name_entry = name_en.get()
        day_end_entry = day_end_en.get()
        quot_entry = quot_en.get()
        min_quot_entry = min_quot_en.get()
        max_quot_entry = max_quot_en.get()
        num_contr_entry = num_contr_en.get()
        if ( date_check(torg_date_entry) and len(name_entry)==11 and name_entry[5]=='-' and
             date_check(day_end_entry) and quot_check(quot_entry) and
             quot_check(min_quot_entry) and quot_check(max_quot_entry) and 
             chrono_check(torg_date_entry, day_end_entry) ):
            name_numeric_part1 = name_entry[:5]
            name_numeric_part2 = name_entry[6:]
            name_numeric_part = name_numeric_part1 + name_numeric_part2
            for symb1 in name_numeric_part:
                if symb1.isnumeric()==False:
                    error_window(root, 'Неправильный формат записи!')
                else:
                    for symb2 in num_contr_entry:
                        if symb2.isnumeric()==False:
                            error_window(root, 'Неправильный формат записи!')
                        else:
                            if int(num_contr_entry)<0:
                                error_window(root, 'Неправильный формат записи!')
                            else:
                                error_window(root, 'Успех')
        else:
            error_window(root, 'Неправильный формат записи!')
               
    edit_new_set = Button( edit_new_wnd, text='Применить', width=12 )
    edit_new_set.place( x=206, y=100 )
    edit_new_set.bind( '<Button-1>', edit_new_set_on )

    #кнопка "Отмена"
    def edit_new_cancel_on(self):
        edit_new_wnd.destroy()
    edit_new_cancel = Button( edit_new_wnd, text='Отмена', width=12 )
    edit_new_cancel.place( x=310, y=100 )
    edit_new_cancel.bind( '<Button-1>', edit_new_cancel_on )
    
    edit_new_wnd.mainloop()

#функция, открывающая окно-уведомление об ошибке
def error_window(root, err_str):
    
    #добавить проверку на существование еще одного окна
    
    error_wnd = Toplevel(root)
    error_wnd.geometry('320x100+420+250')
    error_wnd.title('Ошибка')
    error_wnd.minsize(320,100)
    error_wnd.maxsize(320,100)
    error_msg = Label( error_wnd, text=err_str, anchor='center', width=60 )
    error_msg.place( relx=0.5, rely=0.33, anchor=CENTER )
    
    #кнопка ОК
    def error_ok_on(self):
        error_wnd.destroy()
    error_ok = Button( error_wnd, text='ОК', width=10 )
    error_ok.place( x=125, y=65 )
    error_ok.bind( '<Button-1>', error_ok_on )
    
    error_wnd.mainloop()
