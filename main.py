import os, sys
from dbfunc import *

#считывание логина и пароля из конфига
with open( os.path.dirname(sys.argv[0])+'\\config.txt', 'r' ) as user:
    line_count = 1
    for line in user:
        if line_count==1:
            username = line
        else:
            username_password = line
        line_count = line_count + 1

#создание и настройка окна
root=Tk()                               
root.geometry('1080x445')               
root.title('Фьючерсы')

#загрузка таблицы при старте 
table_format = load_and_filter(username, username_password, '1996-02-05',
                               '1996-10-30', '-не выбрано-', 78.4, 85, 'torg_date', 'по возр.')

#НАДПИСИ
#надпись "Фильтры"
filters_label = Label( root, text='Фильтрация', font=('TkDefaultFont', 12, 'bold'), width=13 )
filters_label.place( x=695, y=10 )
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
#надпись "Изменение"
edit_label = Label( root, text='Изменение', font=('TkDefaultFont', 12, 'bold'), width=13 )
edit_label.place( x=910, y=10 )
#надпись "Удаление записей"
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

#табличная форма
table_out = ScrolledText( root, width=88, height=25, font=('Courier New', 9, 'underline italic bold') )
table_out.insert( 0.1, table_format )
table_out.place( x=10, y=30 )
table_out.configure(state='disabled')

#пользовательский стиль записей и выпадающих списков
entry_style = Style()
entry_style.configure('TEntry', foreground='blue')
combo_style = Style()
combo_style.configure('TCombobox', foreground='blue')

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
        edit_check_label = Label( root, 
                                  text=max_row,
                                  font=('TkDefaultFont', 9),
                                  width=30 )
        edit_check_label.place( x=984, y=270 )
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

#обработчик закрытия окна
def root_close():
    childs = root.place_slaves()
    for obj in childs:
        obj.destroy()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", root_close)  #обработка закрытия окна
root.mainloop()                                #удержание окна
