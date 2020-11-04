import sys, os, datetime, csv, mysql.connector
from tkinter import *
from tkinter.ttk import *
from tktbl import *
from tkcalendar import *
    
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
        get_table = mysql.connector.connect( host = 'localhost',
                                             database = 'fut_cen_bum',
                                             user = self.username,
                                             password = self.password )
        get_table._open_connection()
        load_table = get_table.cursor()
        load_table.execute( 'SELECT * FROM f_zb ' 
			    'INTO OUTFILE \'C:/temp/out.csv\' '
			    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' '
			    'LINES TERMINATED BY \'\n\';' )
        load_table.close()
        get_table.close()
        #переименовать заголовки
        with open( 'C:\\temp\\out.csv', 'r+', newline='' ) as tablefile:
            add_headers = csv.reader( tablefile )
            headers = 'Дата торг.,Код фьюч.,Дата погаш.,Тек.цена,Мин.цена,Макс.цена,Число прод.\n'
            for row in add_headers:
                headers += ','.join(row) + '\n'
        with open( 'C:\\temp\\out.csv', 'w+', newline = '' ) as tablefile:
            tablefile.write( headers )
        self.table = MyTableCanvas( self.tableframe, self.tablemodel, cols=7, height=395, width=700,
                                    cellbackgr='white', thefont=('TkDefault',10),
                                    rowselectedcolor='blue', editable=True )
        self.table.adjustColumnWidths()
        self.table.importCSV( 'C:\\temp\\out.csv' )
        self.table.show()

class TableWnd:
    def __init__( self, master, username, password, filterdates, fut_names, filterquotes ):
        self.master = master
        self.username = username
        self.password = password
        self.filterdates = filterdates
        self.fut_names = fut_names
        self.filterquotes = filterquotes
        
        self.table_wnd = Toplevel( self.master )
        self.table_wnd.geometry( '1000x445+160+140' )
        self.table_wnd.title( 'Фьючерсы' )
        self.table_wnd.resizable( width=False, height=False )
        self.tableframe = Frame( self.table_wnd, width=700, height=445 )
        self.tableframe.place( x=10, y=10 )
        self.main_table = MainTable( self.master, self.tableframe, self.username, self.password )
        #главное меню
        self.main_menu = Menu( self.table_wnd )
        self.table_wnd.config( menu=self.main_menu )
        self.main_menu.add_command( label='Основные показатели', command=self.log_on )
        self.main_menu.add_command( label='Статистические характеристики', command=self.stat_on )
        self.main_menu.add_command( label='Проверка нормальности', command=self.norm_on )
        self.main_menu.add_command( label='Помощь', command=self.help_on )
        #фрейм "Фильтрация"
        self.filters_label = Label( self.table_wnd, text='Фильтрация', font=('TkDefaultFont', 12, 'bold'), width=11 )
        self.filters_frame = LabelFrame( self.table_wnd, width=264, height=425, labelwidget=self.filters_label, labelanchor='n', text='Фильтрация')
        self.filters_frame.place( x=785, y=10 )
        #надпись "Диапазон по дате торгов"
        self.torg_date_label = Label( self.table_wnd, text='Диапазон по дате торгов', font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.torg_date_label.place( x=795, y=40 )
        #надпись "По имени фьючерса"
        self.name_label = Label( self.table_wnd, text='По имени фьючерса', font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.name_label.place( x=795, y=92 )
        #надпись "Диапазон по котировке"
        self.quot_label = Label( self.table_wnd, text='Диапазон по тек. цене', font=('TkDefaultFont', 9, 'underline'), width=24 )
        self.quot_label.place( x=795, y=144 )
        #крайние даты для фильтрования
        self.mindate = datetime.date.fromisoformat( self.filterdates[0] )
        self.maxdate = datetime.date.fromisoformat( self.filterdates[1] )
        #левая граница даты
        self.torg_date_from = DateEntry( self.table_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                         firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                         maxdate=self.maxdate, year=self.mindate.year, month=self.mindate.month,
                                         day=self.mindate.day, showweeknumbers=False )
        self.torg_date_from.config( state="readonly" )
        self.torg_date_from.place( x=795, y=62 )
        #правая граница даты
        self.torg_date_to = DateEntry( self.table_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                       firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                       maxdate=self.maxdate, showweeknumbers=False )
        self.torg_date_to.config( state="readonly" )
        self.torg_date_to.place( x=883, y=62 )
        #список с выбором имени фьючерса
        self.name_menu = Combobox( self.table_wnd, state="readonly" )
        self.name_menu['values'] = tuple( self.fut_names )
        self.name_menu.current(0)
        self.name_menu.place( x=795, y=114, width=176 )
        #текстовое поле для ввода левой границы котировки
        self.quot_from = Entry( self.table_wnd, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.quot_from.insert( 0, self.filterquotes[0] )
        self.quot_from.place( x=795, y=166 )
        #текстовое поле для ввода правой границы котировки
        self.quot_to = Entry( self.table_wnd, width=10, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.quot_to.insert( 0, self.filterquotes[1] )
        self.quot_to.place( x=883, y=166 )
        #кнопка "Применить фильтры"
        self.append = Button( self.table_wnd, text='Применить фильтры', width=22, command=self.append_on )
        self.append.place( x=847, y=360 )
        #кнопка "Сбросить фильтры"
        self.clear = Button( self.table_wnd, text='Сбросить фильтры', width=22, command=self.clear_on )
        self.clear.place( x=847, y=395 )
        #обработка закрытия окна
        self.table_wnd.protocol( 'WM_DELETE_WINDOW', self.master.destroy )

    #кнопка "Применить фильтры"
    def append_on(self):               
        l_date = self.torg_date_from.get()
        r_date = self.torg_date_to.get()
        l_quot = self.quot_from.get()
        r_quot = self.quot_to.get()
        if not quot_check( l_quot ) or not quot_check( r_quot ):
            messagebox.showerror( 'Ошибка', 'Неправильно введена котировка!' )
        else:
            l_quot = l_quot.replace( ',','.' )
            r_quot = r_quot.replace( ',','.' )
            if float( l_quot ) > float( r_quot ):
                messagebox.showerror( 'Ошибка', 'Неправильно введена котировка!' )

    #кнопка "Сбросить фильтры"
    def clear_on(self):
        self.torg_date_from.delete( 0, END )
        self.torg_date_from.insert( 0, self.filterdates[0] )      #поставить раннюю дату
        self.torg_date_to.delete( 0, END )
        self.torg_date_to.insert( 0, self.filterdates[1] )        #поставить самую позднюю дату
        self.quot_from.delete( 0, END )
        self.quot_from.insert( 0, self.filterquotes[0] )                    #поставить минимальное число
        self.quot_to.delete( 0, END )
        self.quot_to.insert( 0, self.filterquotes[1] )                      #поставить максимальное число

    #пункты меню 
    def log_on(self):
        self.log_wnd = Toplevel(self.master)
        self.log_wnd.geometry('700x400+360+170')
        self.log_wnd.title('Расчет логарифма изменения однодневной процентной ставки за два торговых дня')
        self.log_wnd.resizable( width=False, height=False )
        self.log_wnd.grab_set()                 #главное окно неактивно
        self.log_wnd.focus_set()
    def stat_on(self):
        self.stat_wnd = Toplevel(self.master)
        self.stat_wnd.geometry('700x400+360+170')
        self.stat_wnd.title('Расчет основных статистических характеристик')
        self.stat_wnd.resizable( width=False, height=False )
        self.stat_wnd.grab_set()                #главное окно неактивно
        self.stat_wnd.focus_set()
    def norm_on(self):
        self.norm_wnd = Toplevel(self.master)
        self.norm_wnd.geometry('700x400+360+170')
        self.norm_wnd.title('Проверка нормальности контролируемого показателя')
        self.norm_wnd.resizable( width=False, height=False )
        self.norm_wnd.grab_set()                #главное окно неактивно      
        self.norm_wnd.focus_set()
    def help_on(self):
        self.help_wnd = Toplevel(self.master)
        self.help_wnd.geometry('700x400+360+170')
        self.help_wnd.title('Помощь' )
        self.help_wnd.resizable( width=False, height=False )
        self.help_wnd.grab_set()                #главное окно неактивно
        self.help_wnd.focus_set()

class MainWnd():
    filterdates = ['empty']
    filterquotes = ['empty']
    fut_names = ['-не выбрано-']
    username = ''
    password = ''
    def __init__(self):
        #создание окна с запросом пароля и логина
        self.master = Tk()
        #пользовательский стиль записей и выпадающих списков
        self.entry_style = Style()
        self.entry_style.configure( 'TEntry', foreground='blue' )
        self.combo_style = Style()
        self.combo_style.configure( 'TCombobox', foreground='blue' )
        self.master.resizable( width=False, height=False )
        self.master.geometry( '280x130+530+300' )
        self.master.title( 'Авторизация' )
        self.master.resizable( width=False, height=False )
        #пояснение к окну
        self.loginpswd_label = Label( self.master, text='Введите логин и пароль от сервера MySQL:', font=('TkDefaultFont', 9), width=40 )
        self.loginpswd_label.place( x=16, y=5 )
        #ввод логина
        self.login_label = Label( self.master, text='Логин:', font=('TkDefaultFont', 9, 'underline'), width=7 )
        self.login_label.place( x=10, y=30 )
        self.login_entry = Entry( self.master, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.login_entry.place( x=65, y=30 )
        self.login_entry.insert( 0, 'root' )
        #ввод пароля
        self.password_label = Label( self.master, text='Пароль:', font=('TkDefaultFont', 9, 'underline'), width=7 )
        self.password_label.place( x=10, y=60 )
        self.password_entry = Entry( self.master, width=24, style='entry_style.TEntry', font=('Courier New', 10, 'bold') )
        self.password_entry.place( x=65, y=60 )
        #кнопка авторизация "ОК" 
        self.auth_ok = Button( self.master, text='ОК', width=8, command=self.auth_ok )
        self.auth_ok.place( x=70, y=95 )
        #кнопка авторизация "Выход"
        self.auth_cancel = Button( self.master, text='Выход', width=8, command=self.master.destroy )
        self.auth_cancel.place( x=150, y=95 )
        #обработка закрытия окна
        self.master.protocol( 'WM_DELETE_WINDOW', self.master.destroy )
        self.master.mainloop()

    #проверка и запись пароля и логина
    def auth_ok(self):
        login = self.login_entry.get()
        pswrd = self.password_entry.get()
        try:
            #удаление файла с таблицей, если он существует
            check_login_pswd = mysql.connector.connect( host = 'localhost',
                                                        database = 'fut_cen_bum',
                                                        user = login,
                                                        password = pswrd )
            #check_login_pswd._open_connection()
            check_login_pswd.close()
        except mysql.connector.Error:
            messagebox.showerror('Ошибка', 'Неправильный логин или пароль!')
        else:
            self.username = login
            self.password = pswrd
            #загрузка параметров фильтра
            if os.path.exists('C:\\temp\\maxmin.csv'):
                os.remove('C:\\temp\\maxmin.csv')
            if os.path.exists('C:\\temp\\fnames.csv'):
                os.remove('C:\\temp\\fnames.csv')
            get_filter = mysql.connector.connect( host = 'localhost',
                                                  database = 'fut_cen_bum',
                                                  user = self.username,
                                                  password = self.password )
            get_filter._open_connection()
            load_filter = get_filter.cursor()
            load_filter.callproc( 'max_min_distinct' )
            load_filter.close()
            get_filter.close()
            with open( 'C:\\temp\\maxmin.csv', 'r+', newline='' ) as maxminfile:
                date_quot_read = csv.reader( maxminfile, quotechar='"' )
                date_quot_read = list( date_quot_read )
                self.filterdates = [ ''.join( date_quot_read[0] ), ''.join( date_quot_read[2] ) ]
                self.filterquotes = [ ''.join( date_quot_read[1] ), ''.join( date_quot_read[3] ) ]
            with open( 'C:\\temp\\fnames.csv', 'r+', newline='' ) as fnamesfile:
                fnames_read = csv.reader( fnamesfile, quotechar='"' )
                for row in fnames_read:
                    self.fut_names += row
            self.master.withdraw()
            self.table_window = TableWnd( self.master, self.username, self.password,
                                          self.filterdates, self.fut_names, self.filterquotes )

def main():   
    root = MainWnd()

if __name__ == "__main__":
    main()
