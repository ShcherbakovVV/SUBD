import mysql.connector
from tkinter import *

#вместо 0000 указать свой пароль, указанный при установке MySQl
db_connect = mysql.connector.connect( host = 'localhost',
                                      database = 'fut_cen_bum',
                                      user = 'root',
                                      password = '0000' )

root=Tk()                    #создание окна

root.geometry('1000x600')    #размер окна
root.title('Фьючерсы')       #заголовок окна

#надпись "Фильтры"
filters = Label( root, text='Фильтры', width=7, height=1 )
filters.place( x=670, y=30 )

#надпись "По дате торгов"
date_torg = Label( root, text='По дате торгов', width=14, height=1 )
date_torg.place( x=612, y=60 )

#надпись "ОТ (по дате)"
ot_date = Label( root, text='ОТ', width=2, height=1 )
ot_date.place( x=620, y=90 )

#текстовое поле для ввода левой границы даты
date_torg_from = Text( root, width=6, height=1 )
date_torg_from.place( x=642, y=90 )

#надпись "ДО (по дате)"
do_date = Label( root, text='ДО', width=2, height=1 )
do_date.place( x=700, y=90 )

#текстовое поле для ввода правой границы даты
date_torg_to = Text( root, width=6, height=1 )
date_torg_to.place( x=722, y=90 )

#надпись "По имени фьючерса"
name = Label( root, text='По имени фьючерса', width=17, height=1 )
name.place( x=617, y=120 )

#список с выбором имени фьючерса
name_sel = StringVar(root)
name_sel.set('-Выберите фьючерс-')
name = OptionMenu( root, name_sel, '-Выберите фьючерс-', 'тест1', 'тест2', 'тест3' )
name.place( x=620, y=148 )

#надпись "По котировке"
quot = Label( root, text='По котировке', width=17, height=1 )
quot.place( x=617, y=180 )

#надпись "ОТ (по котировке)"
ot_quot = Label( root, text='ОТ', width=2, height=1 )
ot_quot.place( x=620, y=210 )

#текстовое поле для ввода левой границы котировки
quot_from = Text( root, width=6, height=1 )
quot_from.place( x=642, y=210 )

#надпись "ДО (по котировке)"
do_quot = Label( root, text='ДО', width=2, height=1 )
do_quot.place( x=700, y=210 )

#текстовое поле для ввода правой границы котировки
quot_to = Text( root, width=6, height=1 )
quot_to.place( x=722, y=210 )

#кнопка "Применить фильтр"
append = Button( root, text='Применить фильтр', width=20, height=1 )
append.place( x=628, y=270 )



height = 5
width = 5
cells = {}
for i in range(height): #Rows
    for j in range(width): #Columns
        b = Entry(root, text="")
        b.grid(row=i, column=j)
        cells[(i,j)] = b



#кнопка "Восстановить таблицу"
restore = Button( root, text='Восстановить таблицу', width=20, height=1 )
restore.place( x=800, y=60 )

#кнопка "Новая запись"
newentry = Button( root, text='Новая запись', width=20, height=1 )
newentry.place( x=800, y=90 )

#кнопка "Удалить запись"
delentry = Button( root, text='Удалить запись', width=20, height=1 )
delentry.place( x=800, y=120 )

#кнопка "Редактировать запись"
editentry = Button( root, text='Редактировать запись', width=20, height=1 )
editentry.place( x=800, y=150 )

db_connect.close()                               
root.mainloop()              #удержание окна
