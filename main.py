from dbfunc import *

#путь к этому скрипту
#PATH = os.path.dirname(sys.argv[0])
#PATH.replace('\\\\', '\\')

#создание и настройка окна
root=Tk()                               
root.geometry('1000x445')               
root.title('Фьючерсы')

#загрузка таблицы при старте 
load_and_filter(root, '1996-02-05', '1996-10-30', 'NOT_SET', 78.4, 85)

#НАДПИСИ
#надпись "Фильтры"
filters_label = Label( root, text='Фильтрация', font=('TkDefaultFont', 12, 'bold'), width=13 )
filters_label.place( x=685, y=10 )
#надпись "Диапазон по дате торгов"
date_torg_label = Label( root, text='Диапазон по дате торгов', font=('TkDefaultFont', 9, 'underline'), width=24 )
date_torg_label.place( x=655, y=40 )
#date_torg_label.configure(underline=True)
#надпись "По имени фьючерса"
name_label = Label( root, text='По имени фьючерса', font=('TkDefaultFont', 9, 'underline'), width=24 )
name_label.place( x=655, y=92 )
#надпись "Диапазон по котировке"
quot_label = Label( root, text='Диапазон по котировке', font=('TkDefaultFont', 9, 'underline'), width=24 )
quot_label.place( x=655, y=142 )

entry_style = Style()
entry_style.configure('TEntry', foreground='blue')

#текстовое поле для ввода левой границы даты
date_torg_from = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
date_torg_from.place( x=655, y=62 )
#date_torg_from.insert(0, 'yyyy-mm-dd')           #поставить раннюю дату
date_torg_from.insert(0, '1996-02-05') 

#текстовое поле для ввода правой границы даты
date_torg_to = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
date_torg_to.place( x=745, y=62 )
#date_torg_to.insert(0, 'yyyy-mm-dd')            #поставить самую позднюю дату.
date_torg_to.insert(0, '1996-10-30')

#список с выбором имени фьючерса
name_menu = Combobox( root )
name_menu['values'] = ('-Выберите фьючерс-', 'тест1', 'тест2', 'тест3')
name_menu.current(0)
name_menu.place( x=655, y=114 )

#текстовое поле для ввода левой границы котировки
quot_from = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
quot_from.place( x=655, y=164 )
#quot_from.insert(0, '0')                        #поставить минимальное число
quot_from.insert(0, '78.4')    

#текстовое поле для ввода правой границы котировки
quot_to = Entry( root, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
quot_to.place( x=745, y=164 )
#quot_to.insert(0, '0')                          #поставить максимальное число
quot_to.insert(0, '85')

#кнопка "Применить фильтры"
def append_on(self):               #записывает введенные значения в переменны
    
    #проверка даты
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
            
    #загрузка таблицы
    load_and_filter(root, l_date, r_date, name, l_quot, r_quot)
    
append = Button( root, text='Применить фильтры', width=22 )
append.place( x=655, y=270 )
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
clear.place( x=655, y=300 )
clear.bind( '<Button-1>', clear_on )

#отображение заголовков колонок таблицы
table_header = Text( root, width=88, height=1, font=('Courier New', 9, 'bold') )
table_header.insert(0.1,'  №  │Дата торг. │Код фьюч.    │Дата погаш.│Тек.цена │Мин.цена │Макс.цена  │Число прод.')
table_header.place( x=10, y=10 )
table_header.configure(state='disabled')

#кнопка "Новая запись"
newentry = Button( root, text='Новая запись', width=22 )
newentry.place( x=840, y=60 )

#кнопка "Удалить запись"
delentry = Button( root, text='Удалить запись', width=22 )
delentry.place( x=840, y=90 )

#кнопка "Редактировать запись"
editentry = Button( root, text='Редактировать запись', width=22 )
editentry.place( x=840, y=120 )

#обработчик закрытия окна
def root_close():
    childs = root.place_slaves()
    for obj in childs:
        obj.destroy()
root.protocol("WM_DELETE_WINDOW", root_close)  #обработка закрытия окна
root.mainloop()                                #удержание окна
