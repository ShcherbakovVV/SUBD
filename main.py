import sys
import datetime
from dbfunc import *
from tkintertable import *
from tkcalendar import *

#пользовательская модификация классов Tkintertable
class MyColumnHeader(ColumnHeader):
    def popupMenu(self, event):
        """Add left and right click behaviour for column header"""

        colname = self.model.columnNames[self.table.currentcol]
        collabel = self.model.columnlabels[colname]
        currcol = self.table.currentcol
        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()
        popupmenu.add_command(label="По возрастанию", command=lambda : self.table.sortTable(currcol))
        popupmenu.add_command(label="По убыванию", command=lambda : self.table.sortTable(currcol,reverse=1))

        popupmenu.bind("<FocusOut>", popupFocusOut)
        #self.bind("<Button-3>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

class MyTableCanvas(TableCanvas):
    def addRows(self, num=None):
        if num == None:
            num = simpledialog.askinteger("Сколько записей?",
                                            "Количество записей",initialvalue=1,
                                             parent=self.parentframe)
        if not num:
            return
        keys = self.model.autoAddRows(num)
        self.redrawTable()
        self.setSelectedRow(self.model.getRecordIndex(keys[0]))
        return
    
    def deleteRow(self):
        if len(self.multiplerowlist)>1:
            n = messagebox.askyesno("Удаление",
                                      "Удалить выбранные записи?",
                                      parent=self.parentframe)
            if n == True:
                rows = self.multiplerowlist
                self.model.deleteRows(rows)
                self.clearSelected()
                self.setSelectedRow(0)
                self.redrawTable()
        else:
            n = messagebox.askyesno("Удаление",
                                      "Удалить эту запись?",
                                      parent=self.parentframe)
            if n:
                row = self.getSelectedRow()
                self.model.deleteRow(row)
                self.setSelectedRow(row-1)
                self.clearSelected()
                self.redrawTable()
        return    
    
    def popupMenu(self, event, rows=None, cols=None, outside=None):
        defaultactions = {"Новая запись" : lambda : self.addRows(),
                          "Удалить записи" : lambda : self.deleteRow(),
                          "Filter Records" : self.showFilteringBar,}
        general = ["Новая запись" , "Удалить записи", "Filter Records"]

        def createSubMenu(parent, label, commands):
            menu = Menu(parent, tearoff = 0)
            popupmenu.add_cascade(label=label,menu=menu)
            for action in commands:
                menu.add_command(label=action, command=defaultactions[action])
            return menu

        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()

        if outside == None:
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
            def add_defaultcommands():
                """now add general actions for all cells"""
                for action in main:
                    if action == 'Fill Down' and (rows == None or len(rows) <= 1):
                        continue
                    if action == 'Fill Right' and (cols == None or len(cols) <= 1):
                        continue
                    else:
                        popupmenu.add_command(label=action, command=defaultactions[action])
                return

        for action in general:
            popupmenu.add_command(label=action, command=defaultactions[action])

        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

    def show(self, callback=None):
        self.tablerowheader = RowHeader(self.parentframe, self, width=self.rowheaderwidth)
        self.tablecolheader = MyColumnHeader(self.parentframe, self)
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand'] = self.Xscrollbar.set
        self.tablerowheader['yscrollcommand'] = self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.tablerowheader.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

        self.adjustColumnWidths()
        self.redrawTable(callback=callback)
        self.parentframe.bind("<Configure>", self.redrawVisible)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)
        return

    def updateModel(self, model):
        self.model = model
        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        self.tablewidth = (self.cellwidth)*self.cols
        self.tablecolheader = MyColumnHeader(self.parentframe, self)
        self.tablerowheader = RowHeader(self.parentframe, self)
        self.createTableFrame()
        return

class AuthWnd():
    username = ''
    password = ''
    auth_passed = False                         #пройдена ли процедура аутентификации
    def __init__(self, master, mainframe):
        #создание окна с запросом пароля и логина
        self.master = master
        self.mainframe = mainframe
        self.auth_wnd = Toplevel(self.master)
        self.auth_wnd.geometry('280x130+570+300')
        self.auth_wnd.title('Авторизация')
        self.auth_wnd.minsize(280,130)
        self.auth_wnd.maxsize(280,130)
        #пояснение к окну
        self.loginpswd_label = Label( self.auth_wnd, text='Введите логин и пароль от сервера MySQL:', font=('TkDefaultFont', 9), width=40 )
        self.loginpswd_label.place( x=16, y=5 )
        #ввод логина
        self.login_label = Label( self.auth_wnd, text='Логин:', font=('TkDefaultFont', 9, 'underline'), width=7 )
        self.login_label.place( x=10, y=30 )
        self.login_entry = Entry( self.auth_wnd, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.login_entry.place( x=65, y=30 )
        self.login_entry.insert(0, 'root')
        #ввод пароля
        self.password_label = Label( self.auth_wnd, text='Пароль:', font=('TkDefaultFont', 9, 'underline'), width=7 )
        self.password_label.place( x=10, y=60 )
        self.password_entry = Entry( self.auth_wnd, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.password_entry.place( x=65, y=60 )
        #кнопка авторизация "ОК" 
        self.auth_ok = Button( self.auth_wnd, text='ОК', width=8, command=self.auth_ok )
        self.auth_ok.place( x=70, y=95 )
        #кнопка авторизация "Выход"
        self.auth_cancel = Button( self.auth_wnd, text='Выход', width=8, command=self.master.destroy )
        self.auth_cancel.place( x=150, y=95 )
        #обработка закрытия окна
        self.auth_wnd.protocol( 'WM_DELETE_WINDOW', self.master.destroy )

    #проверка и запись пароля и логина
    def auth_ok(self):
        login = self.login_entry.get()
        pswrd = self.password_entry.get()
        try:
            #удаление файла с таблицей, если он существует
            check_login_pswd = mysql.connector.connect( host = 'localhost',
                                                        database ='fut_cen_bum',
                                                        user = login,
                                                        password = pswrd )
            check_login_pswd._open_connection()
            check_login_pswd.close()
        except mysql.connector.Error:
            messagebox.showerror('Ошибка', 'Неправильный логин или пароль!')
        else:
            self.auth_passed = True
            self.username = login
            self.password = pswrd
            self.main_table = MainTable( self.master, self.mainframe, self.username, self.password )
            self.master.update()
            self.master.deiconify()
            self.auth_wnd.destroy()
    
class MainTable():
    def __init__( self, master, tableframe, username, password ):
        self.master = master
        self.tableframe = tableframe
        self.username = username
        self.password = password
        self.tablemodel = TableModel( rows=1000, columns=7 )
        #загрузка таблицы в файл при старте
        if os.path.exists('C:\\temp\\out.csv'):
            os.remove('C:\\temp\\out.csv')
        load_table = mysql.connector.connect( host = 'localhost',
                                              database = 'fut_cen_bum',
                                              user = self.username,
                                              password = self.password )
        load_table._open_connection()
        load_cursor = load_table.cursor()
        load_cursor.callproc( 'filtr', ('1996-02-05', '1996-10-30', '-не выбрано-',
                                         78.4, 85, 'torg_date', 'по возр.') )
        load_cursor.close()
        load_table.close()
        #если csv файла не существует
        if os.path.exists('C:\\temp\\out.csv'):
            #переименовать заголовки
            with open( 'C:\\temp\\out.csv', 'r+' ) as tablefile:
                add_headers = csv.reader( tablefile )
                headers = 'Дата торг.,Код фьюч.,Дата погаш.,Тек.цена,Мин.цена,Макс.цена,Число прод.\n'
                for row in add_headers:
                    headers += ','.join(row) + '\n'
            with open( 'C:\\temp\\out.csv', 'w+', newline = '' ) as tablefile:
                tablefile.write( headers )
            self.table = MyTableCanvas( self.tableframe, self.tablemodel, cols=7, height=395, width=700,
                                      cellbackgr='white', thefont=('TkDefault',10),
                                      rowselectedcolor='blue', editable=True)
            self.table.adjustColumnWidths()
            self.table.importCSV( 'C:\\temp\\out.csv' )
            self.table.show()
        else:
            self.errwnd = messagebox.showerror('Ошибка', 'Ошибка импорта таблицы - нет .csv-файла!')
            self.errwnd.protocol( 'WM_DELETE_WINDOW', self.master.destroy )   

class MainWnd:
    def __init__(self):
        self.master = Tk()
        #пользовательский стиль записей и выпадающих списков
        self.entry_style = Style()
        self.entry_style.configure('TEntry', foreground='blue')
        self.combo_style = Style()
        self.combo_style.configure('TCombobox', foreground='blue')
    
        self.master.geometry( '1100x445+140+120' )               
        self.master.title( 'Фьючерсы' )
        self.master.withdraw()
        self.tableframe = Frame( self.master, width=700, height=445 )
        self.tableframe.place( x=10, y=10 )

        #главное меню
        self.main_menu = Menu(self.master)
        self.master.config( menu=self.main_menu )
        self.main_menu.add_command( label='Основные показатели', command=self.log_on )
        self.main_menu.add_command( label='Статистические характеристики', command=self.stat_on )
        self.main_menu.add_command( label='Проверка нормальности', command=self.norm_on )
        self.main_menu.add_command( label='Помощь', command=self.help_on )

        #фрейм "Фильтрация"
        self.filters_label = Label( self.master, text='Фильтрация', font=('TkDefaultFont', 12, 'bold'), width=11 )
        self.filters_frame = LabelFrame( self.master, width=264, height=425, labelwidget=self.filters_label,
                                         labelanchor='n', text='Фильтрация')
        self.filters_frame.place( x=785, y=10 )
        #надпись "Диапазон по дате торгов"
        self.torg_date_label = Label( self.master, text='Диапазон по дате торгов',
                                      font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.torg_date_label.place( x=795, y=40 )
        #надпись "По имени фьючерса"
        self.name_label = Label( self.master, text='По имени фьючерса',
                                 font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.name_label.place( x=795, y=92 )
        #надпись "Диапазон по котировке"
        self.quot_label = Label( self.master, text='Диапазон по тек. цене',
                                 font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.quot_label.place( x=795, y=144 )
        #крайние даты для фильтрования
        self.mindate = datetime.date(year=1995, month=2, day=1)
        self.maxdate = datetime.date(year=1996, month=3, day=1)
        #левая граница даты
        self.torg_date_l = DateEntry( self.master, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                      firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                      maxdate=self.maxdate, year=self.mindate.year, month=self.mindate.month,
                                      day=self.mindate.day, showweeknumbers=False )
        self.torg_date_l.config(state="readonly")
        self.torg_date_l.place( x=795, y=62 )
        #правая граница даты
        self.torg_date_r = DateEntry( self.master, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                      firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                      maxdate=self.maxdate, showweeknumbers=False )
        self.torg_date_r.config(state="readonly")
        self.torg_date_r.place( x=883, y=62 )
        #список с выбором имени фьючерса
        self.name_menu = Combobox( self.master, state="readonly" )
        self.name_menu['values'] = ('-не выбрано-', '22020-1503')
        self.name_menu.current(0)
        self.name_menu.place( x=795, y=114, width=176 )
        #текстовое поле для ввода левой границы котировки
        self.quot_from = Entry( self.master, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.quot_from.insert(0, '78.4')
        self.quot_from.place( x=795, y=166 )
        #текстовое поле для ввода правой границы котировки
        self.quot_to = Entry( self.master, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.quot_to.insert(0, '85')
        self.quot_to.place( x=883, y=166 )

        #кнопка "Применить фильтры"
        self.append = Button( self.master, text='Применить фильтры', width=22, command=self.append_on )
        self.append.place( x=847, y=360 )
        #кнопка "Сбросить фильтры"
        self.clear = Button( self.master, text='Сбросить фильтры', width=22, command=self.clear_on )
        self.clear.place( x=847, y=395 )

        self.auth_window = AuthWnd( self.master, self.tableframe )
        #обработка закрытия окна
        self.master.protocol( 'WM_DELETE_WINDOW', self.master.destroy )
        #удержание окна
        self.master.mainloop()

    #кнопка "Применить фильтры"
    def append_on(self):               
        #проверка даты
        l_date = self.torg_date_from.get()
        r_date = self.torg_date_to.get()
        if chrono_check(l_date, r_date)==False:
            messagebox.showerror('Ошибка', 'Неправильно введена дата!')
        #доделать с выбором имени фьючерса
        if self.name_menu.get()=='-не выбрано-':
            name = '-не выбрано-'
        else:
            name = '22020-1503'
        #проверка котировок   
        l_quot = self.quot_from.get()
        r_quot = self.quot_to.get()
        if quot_check(l_quot)==False or quot_check(r_quot)==False:
            messagebox.showerror('Ошибка', 'Неправильно введена котировка!')
        else:
            l_quot = l_quot.replace(',','.')
            r_quot = r_quot.replace(',','.')
            if float(l_quot)>float(r_quot):
                messagebox.showerror('Ошибка', 'Неправильно введена котировка!')
        #отображение таблицы

    #кнопка "Сбросить фильтры"
    def clear_on(self):
        self.torg_date_from.delete(0, END)
        self.torg_date_from.insert(0, 'yyyy-mm-dd')      #поставить раннюю дату
        self.torg_date_to.delete(0, END)
        self.torg_date_to.insert(0, 'yyyy-mm-dd')        #поставить самую позднюю дату
        self.quot_from.delete(0, END)
        self.quot_from.insert(0, '0')                    #поставить минимальное число
        self.quot_to.delete(0, END)
        self.quot_to.insert(0, '0')                      #поставить максимальное число

    #пункты меню 
    def log_on(self):
        self.log_wnd = Toplevel(self.master)
        self.log_wnd.geometry('700x400+360+170')
        self.log_wnd.title('Расчет логарифма изменения однодневной процентной ставки за два торговых дня')
        self.log_wnd.minsize(700,400)
        self.log_wnd.maxsize(700,400)
        self.log_wnd.grab_set()                 #главное окно неактивно
        self.log_wnd.focus_set()
    def stat_on(self):
        self.stat_wnd = Toplevel(self.master)
        self.stat_wnd.geometry('700x400+360+170')
        self.stat_wnd.title('Расчет основных статистических характеристик')
        self.stat_wnd.minsize(700,400)
        self.stat_wnd.maxsize(700,400)
        self.stat_wnd.grab_set()                #главное окно неактивно
        self.stat_wnd.focus_set()
    def norm_on(self):
        self.norm_wnd = Toplevel(self.master)
        self.norm_wnd.geometry('700x400+360+170')
        self.norm_wnd.title('Проверка нормальности контролируемого показателя')
        self.norm_wnd.minsize(700,400)
        self.norm_wnd.maxsize(700,400)
        self.norm_wnd.grab_set()                #главное окно неактивно      
        self.norm_wnd.focus_set()
    def help_on(self):
        self.help_wnd = Toplevel(self.master)
        self.help_wnd.geometry('700x400+360+170')
        self.help_wnd.title('Помощь' )
        self.help_wnd.minsize(700,400)
        self.help_wnd.maxsize(700,400)
        self.help_wnd.grab_set()                #главное окно неактивно
        self.help_wnd.focus_set()
        
def main():   
    root = MainWnd()

if __name__ == "__main__":
    main()
