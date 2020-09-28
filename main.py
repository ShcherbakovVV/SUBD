import sys, os, csv, mysql.connector
from tkinter import *
from tkinter.ttk import *

#создание и настройка окна
root=Tk()                               
root.geometry('1000x600')               
root.title('Фьючерсы')    

#соединение с базой данных
#вместо 0000 указать свой пароль, указанный при установке MySQl
#также необходимо закомментировать (решеткой) строку, начинающуюся "secure-file-priv"
#в файле C:\ProgramData\MySQL\MySQL Server 8.0\my.ini (от имени администратора)
db = mysql.connector.connect( host='localhost',
                              database='fut_cen_bum',
                              user='root',
                              password='0000' )

#путь к этому скрипту
PATH = os.path.dirname(sys.argv[0])
#PATH.replace('\\\\', '\\')

#открытие файла с таблицей
#with open( 'table.csv' ) as tablefile:
   # table = csv.reader( tablefile )

#взаимодействие с MySQL - экспорт таблицы в csv
cursor = db.cursor()
cursor.execute('USE fut_cen_bum')
cursor.execute('SELECT * FROM fut_cen_bum.f_zb INTO OUTFILE \'C:/Users/VS/Desktop/subd/out.csv\''
               ' FIELDS ENCLOSED BY \'"\' TERMINATED BY \';\'  ESCAPED BY \'"\''
               ' LINES TERMINATED BY \'\\n\'')


#надпись "Фильтры"
filters_label = Label( root, text='Фильтры', width=9 )
filters_label.place( x=670, y=30 )

#надпись "По дате торгов"
date_torg_label = Label( root, text='По дате торгов', width=14 )
date_torg_label.place( x=618, y=60 )

#надпись "ОТ (по дате)"
ot_date = Label( root, text='ОТ', width=3 )
ot_date.place( x=620, y=90 )

#текстовое поле для ввода левой границы даты
date_torg_from = Text( root, width=6, height=1 )
date_torg_from.place( x=642, y=90 )
l_date = date_torg_from.get(CURRENT, END)

#надпись "ДО (по дате)"
do_date = Label( root, text='ДО', width=3 )
do_date.place( x=700, y=90 )

#текстовое поле для ввода правой границы даты
date_torg_to = Text( root, width=6, height=1 )
date_torg_to.place( x=722, y=90 )
r_date = date_torg_to.get(CURRENT, END)

#надпись "По имени фьючерса"
name_label = Label( root, text='По имени фьючерса', width=20 )
name_label.place( x=617, y=120 )

#список с выбором имени фьючерса
name_menu = Combobox( root )
name_menu['values'] = ('-Выберите фьючерс-', 'тест1', 'тест2', 'тест3')
name_menu.current(0)
name_menu.place( x=620, y=148 )

#надпись "По котировке"
quot_label = Label( root, text='По котировке', width=17 )
quot_label.place( x=617, y=180 )

#надпись "ОТ (по котировке)"
ot_quot = Label( root, text='ОТ', width=3 )
ot_quot.place( x=620, y=210 )

#текстовое поле для ввода левой границы котировки
quot_from = Text( root, width=6, height=1 )
quot_from.place( x=642, y=210 )
l_quot = quot_from.get(CURRENT, END)

#надпись "ДО (по котировке)"
do_quot = Label( root, text='ДО', width=3 )
do_quot.place( x=700, y=210 )

#текстовое поле для ввода правой границы котировки
quot_to = Text( root, width=6, height=1 )
quot_to.place( x=722, y=210 )
r_quot = quot_to.get(CURRENT, END)

#кнопка "Применить фильтр"
def append_on(self):               #записывает введенные значения в переменные
    l_date = date_torg_from.get( '0.1', END)
    r_date = date_torg_to.get( '0.1', END)
    #доделать с выбором имени фьючерса
    l_quot = quot_from.get( '0.1', END)
    r_quot = quot_to.get( '0.1', END)
append = Button( root, text='Применить фильтр', width=22 )
append.place( x=628, y=270 )
append.bind( '<Button-1>', append_on )

#отображение таблицы
height = 5
width = 5
cells = {}
for i in range(height):                        #строки
    for j in range(width):                     #столбцы
        cell = Entry( root, text="", width=5 )
        cell.grid( row=i, column=j )
        cells[(i,j)] = cell

#кнопка "Восстановить таблицу"
restore = Button( root, text='Восстановить таблицу', width=22 )
restore.place( x=800, y=60 )

#кнопка "Новая запись"
newentry = Button( root, text='Новая запись', width=22 )
newentry.place( x=800, y=90 )

#кнопка "Удалить запись"
delentry = Button( root, text='Удалить запись', width=22 )
delentry.place( x=800, y=120 )

#кнопка "Редактировать запись"
editentry = Button( root, text='Редактировать запись', width=22 )
editentry.place( x=800, y=150 )

db.close()                   #закрытие соединения                    
root.mainloop()              #удержание окна
