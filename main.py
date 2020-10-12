import os, sys
from dbfunc import *

#логин и пароль от сервера MySQL, форматированная таблица
username = ''
username_password = ''
table_format = ''

#выполнение требований MySQL по работе с файлами
if not os.path.exists('C://temp'):
    os.makedirs('C://temp')
#with open( 'C://ProgramData//MySQL//MySQL Server 8.0//my.ini', 'a' ) as cfg: 
   # if cfg.find('secure-file-priv = ')!=-1:
   #     cfg.write('secure-file-priv = ')
   # elif cfg.find('tmpdir = \'C:/temp/\'')!=-1:
   #     cfg.write('tmpdir = \'C:/temp/\'')

#создание и настройка окна
root=Tk()                               
root.geometry('1080x445+140+120')               
root.title('Фьючерсы')

#пользовательский стиль записей и выпадающих списков
entry_style = Style()
entry_style.configure('TEntry', foreground='blue')
combo_style = Style()
combo_style.configure('TCombobox', foreground='blue')

#табличная форма
table_out = ScrolledText( root, width=88, height=25, font=('Courier New', 9, 'underline italic bold') )
table_out.place( x=10, y=30 )

#обработчик закрытия окна
def root_close():
    childs = root.place_slaves()
    for obj in childs:
        obj.destroy()
    root.destroy()

#создание окна с запросом пароля и логина
authorize = Toplevel(root)
authorize.geometry('280x130+570+300')
authorize.title('Авторизация')
authorize.minsize(280,130)
authorize.maxsize(280,130)
authorize.grab_set()                
authorize.attributes('-topmost', 'true')

#пояснение к окну
loginpswd_label = Label( authorize, text='Введите логин и пароль от сервера MySQL:', font=('TkDefaultFont', 9), width=40 )
loginpswd_label.place( x=16, y=5 )

#ввод логина
login_label = Label( authorize, text='Логин:', font=('TkDefaultFont', 9, 'underline'), width=7 )
login_label.place( x=10, y=30 )
login_entry = Entry( authorize, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
login_entry.place( x=65, y=30 )
login_entry.insert(0, 'root')

#ввод пароля
password_label = Label( authorize, text='Пароль:', font=('TkDefaultFont', 9, 'underline'), width=7 )
password_label.place( x=10, y=60 )
password_entry = Entry( authorize, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
password_entry.place( x=65, y=60 )

#кнопка авторизация "ОК" 
def auth_ok_on(self):
    login = login_entry.get()
    pswd = password_entry.get()
    login_pswd_inv = False
    try:
        check_login_pswd = mysql.connector.connect( host='localhost',
                                                    database='fut_cen_bum',
                                                    user=login,
                                                    password=pswd )
        check_login_pswd.close()
    except mysql.connector.Error:
        error_window(root, 'Неправильный логин или пароль!')
        login_pswd_inv = True
    if not login_pswd_inv:
        global username, username_password
        username = login
        username_password = pswd
        
        #загрузка таблицы при старте
        global table_format
        table_format = load_and_filter(username, username_password, '1996-02-05',
                                       '1996-10-30', '-не выбрано-', 78.4, 85, 'torg_date', 'по возр.')
        table_out.insert( 0.1, table_format )
        table_out.configure(state='disabled')
        root.grab_release()
        authorize.attributes('-topmost', 'false')
        authorize.destroy()
        root.attributes('-topmost', 'true')            #приподнятие главного окна
        root.attributes('-topmost', 'false')
auth_ok = Button( authorize, text='ОК', width=8 )
auth_ok.place( x=70, y=95 )
auth_ok.bind( '<Button-1>', auth_ok_on )

#кнопка авторизация "Выход"
def auth_cancel_on(self):
    root_close()
auth_cancel = Button( authorize, text='Выход', width=8 )
auth_cancel.place( x=150, y=95 )
auth_cancel.bind( '<Button-1>', auth_cancel_on )

#обработка закрытия авторизации
def auth_close():
    root_close()
authorize.protocol("WM_DELETE_WINDOW", auth_close)              

#главное меню
main_menu = Menu(root)
root.config( menu=main_menu )

def log_on():
    log_wnd = Toplevel(root)
    log_wnd.geometry('700x400+360+170')
    log_wnd.title('Расчет логарифма изменения однодневной процентной ставки за два торговых дня')
    log_wnd.minsize(700,400)
    log_wnd.maxsize(700,400)
    log_wnd.grab_set()                 #главное окно неактивно
    log_wnd.focus_set()
main_menu.add_command( label='Основные показатели', command=log_on )

def stat_on():
    stat_wnd = Toplevel(root)
    stat_wnd.geometry('700x400+360+170')
    stat_wnd.title('Расчет основных статистических характеристик')
    stat_wnd.minsize(700,400)
    stat_wnd.maxsize(700,400)
    stat_wnd.grab_set()                #главное окно неактивно
    stat_wnd.focus_set()
main_menu.add_command( label='Статистические характеристики', command=stat_on )

def norm_on():
    norm_wnd = Toplevel(root)
    norm_wnd.geometry('700x400+360+170')
    norm_wnd.title('Проверка нормальности контролируемого показателя')
    norm_wnd.minsize(700,400)
    norm_wnd.maxsize(700,400)
    norm_wnd.grab_set()                #главное окно неактивно      
    norm_wnd.focus_set()
main_menu.add_command( label='Проверка нормальности', command=norm_on )

def help_on():
    help_wnd = Toplevel(root)
    help_wnd.geometry('700x400+360+170')
    help_wnd.title('Помощь' )
    help_wnd.minsize(700,400)
    help_wnd.maxsize(700,400)
    help_wnd.grab_set()                #главное окно неактивно
    help_wnd.focus_set()
main_menu.add_command( label='Помощь', command=help_on )

#НАДПИСИ
#фрейм "Фильтрация"
filters_label = Label( root, text='Фильтрация', font=('TkDefaultFont', 12, 'bold'), width=11 )
filters_frame = LabelFrame( root, width=200, height=425, labelwidget=filters_label, labelanchor='n', text='Фильтрация')
filters_frame.place( x=650, y=10 )
#надпись "Диапазон по дате торгов"
torg_date_label = Label( root, text='Диапазон по дате торгов', font=('TkDefaultFont', 9, 'underline'), width=24 )
torg_date_label.place( x=660, y=40 )
#надпись "По имени фьючерса"
name_label = Label( root, text='По имени фьючерса', font=('TkDefaultFont', 9, 'underline'), width=24 )
name_label.place( x=660, y=92 )
#надпись "Диапазон по котировке"
quot_label = Label( root, text='Диапазон по тек. цене', font=('TkDefaultFont', 9, 'underline'), width=24 )
quot_label.place( x=660, y=144 )
#надпись "Упорядочить по"
order_label = Label( root, text='Упорядочить по', font=('TkDefaultFont', 9, 'underline'), width=24 )
order_label.place( x=660, y=196 )
#фрейм "Изменение"
deleditnew_label = Label( root, text='Изменение', font=('TkDefaultFont', 12, 'bold'), width=10 )
deleditnew_frame = LabelFrame( root, width=200, height=425, labelwidget=deleditnew_label, labelanchor='n', text='Изменение')
deleditnew_frame.place( x=860, y=10 )
#надпись "Удаление записи"
delete_entry_label = Label( root, text='Удалить записи', font=('TkDefaultFont', 9, 'underline'), width=24 )
delete_entry_label.place( x=870, y=40 )
#надпись "Изменение записи"
edit_entry_label = Label( root, text='Изменить запись', font=('TkDefaultFont', 9, 'underline'), width=24 )
edit_entry_label.place( x=870, y=144 )
#надпись с примером формата удаления
delete_format_label = Label( root, text='номера записей через пробел', font=('TkDefaultFont', 9), width=30 )
delete_format_label.place( x=868, y=84 )
#надпись "номер записи"
edit_id_label = Label( root, text='№ записи', font=('TkDefaultFont', 9), width=30 )
edit_id_label.place( x=984, y=166 )

#текстовое поле для ввода левой границы даты
torg_date_from = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
torg_date_from.place( x=660, y=62 )
#torg_date_from.insert(0, 'yyyy-mm-dd')           #поставить раннюю дату
torg_date_from.insert(0, '1996-02-05') 

#текстовое поле для ввода правой границы даты
torg_date_to = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
torg_date_to.place( x=750, y=62 )
#torg_date_to.insert(0, 'yyyy-mm-dd')            #поставить самую позднюю дату.
torg_date_to.insert(0, '1996-10-30')

#список с выбором имени фьючерса
name_menu = Combobox( root )
name_menu['values'] = ('-не выбрано-', 'тест1', 'тест2', 'тест3')
name_menu.current(0)
name_menu.place( x=660, y=114, width=178 )

#текстовое поле для ввода левой границы котировки
quot_from = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
quot_from.place( x=660, y=166 )
#quot_from.insert(0, '0')                        #поставить минимальное число
quot_from.insert(0, '78.4')    

#текстовое поле для ввода правой границы котировки
quot_to = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
quot_to.place( x=750, y=166 )
#quot_to.insert(0, '0')                          #поставить максимальное число
quot_to.insert(0, '85')

#список с выбором столбцов
order_column_menu = Combobox( root, style='combo_style.TCombobox', width=11 )
order_column_menu['values'] = ('Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена', 'Мин.цена', 'Макс.цена', 'Число прод.')
order_column_menu.current(0)
order_column_menu.place( x=660, y=218 )

#список с выбором типа сортировки
order_ascdesc_menu = Combobox( root, style='combo_style.TCombobox', width=11 )
order_ascdesc_menu['values'] = ('по возр.', 'по убыв.')
order_ascdesc_menu.current(0)
order_ascdesc_menu.place( x=750, y=218 )

#кнопка "Применить фильтры"
def append_on(self):               #записывает введенные значения в переменны
    
    #проверка даты
    l_date = torg_date_from.get()
    r_date = torg_date_to.get()
    if chrono_check(l_date, r_date)==False:
        error_window(root, 'Неправильно введена дата!')

    #доделать с выбором имени фьючерса
    if name_menu.get()=='-не выбрано-':
        name = '-не выбрано-'
    else:
        name = '22020-1503'
         
    #проверка котировок   
    l_quot = quot_from.get()
    r_quot = quot_to.get()
    if quot_check(l_quot)==False or quot_check(r_quot)==False:
        error_window(root, 'Неправильно введена котировка!')
    else:
        l_quot = l_quot.replace(',','.')
        r_quot = r_quot.replace(',','.')
        if float(l_quot)>float(r_quot):
            error_window(root, 'Неправильно введена котировка!')

    #упорядочивание
    ord_column = order_column_menu.get()
    ord_ascdesc = order_ascdesc_menu.get()

    #отображение таблицы
    table_out.configure(state='normal')
    table_out.delete( 0.1, END )
    table_out.insert( 0.1, load_and_filter(username, username_password, l_date,
                                           r_date, name, l_quot, r_quot, ord_column, ord_ascdesc) )
    table_out.configure(state='disabled')
append = Button( root, text='Применить фильтры', width=22 )
append.place( x=680, y=252 )
append.bind( '<Button-1>', append_on )

#кнопка "Сбросить фильтры"
def clear_on(self):
    torg_date_from.delete(0, END)
    torg_date_from.insert(0, 'yyyy-mm-dd')      #поставить раннюю дату
    torg_date_to.delete(0, END)
    torg_date_to.insert(0, 'yyyy-mm-dd')        #поставить самую позднюю дату
    quot_from.delete(0, END)
    quot_from.insert(0, '0')                    #поставить минимальное число
    quot_to.delete(0, END)
    quot_to.insert(0, '0')                      #поставить максимальное число
clear = Button( root, text='Сбросить фильтры', width=22 )
clear.place( x=680, y=283 )
clear.bind( '<Button-1>', clear_on )

#отображение заголовков колонок таблицы
table_header = Text( root, width=88, height=1, font=('Courier New', 9, 'bold') )
table_header.insert(0.1,'  №  │Дата торг. │Код фьюч.    │Дата погаш.│Тек.цена │Мин.цена │Макс.цена  │Число прод.')
table_header.place( x=10, y=10 )
table_header.configure(state='disabled')

#поле для ввода записей для удаления
delete_entry = Entry( root, width=21, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
delete_entry.place( x=870, y=62 )

#кнопка "Удалить"
def delete_on(self):
    to_delete = delete_entry.get()
    max_row = count_rows( table_out.get(0.1, END) )
    if del_check( to_delete, max_row ): pass
        
    else:
        error_window(root, 'Неправильно указаны номера для удаления!')
delete = Button( root, text='Удалить', width=22 )
delete.place( x=885, y=111 )
delete.bind( '<Button-1>', delete_on )

#текстовое поле для ввода номера изменяемой записи
edit_entry = Entry( root, width=7, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
edit_entry.place( x=983, y=144 )

#кнопка "Изменить"
def edit_on(self):
    to_edit = edit_entry.get()
    max_row = count_rows( table_out.get(0.1, END) )           
    if edit_check( to_edit, max_row ):        
        edit_new_window(root, 'Изменение записи '+to_edit)
    else:
        error_window(root, 'Неправильно введен номер записи!')
edit = Button( root, text='Изменить', width=22 )
edit.place( x=885, y=194 )
edit.bind( '<Button-1>', edit_on )

#кнопка "Новая запись"
def new_on(self):
    edit_new_window(root, 'Новая запись')

new = Button( root, text='Новая запись', width=22 )
new.place( x=885, y=224 )
new.bind( '<Button-1>', new_on )

root.protocol("WM_DELETE_WINDOW", root_close)  #обработка закрытия окна
root.mainloop()                                #удержание окна
