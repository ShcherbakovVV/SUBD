import sys, os, datetime, csv, mysql.connector
from tkinter import *
from tkinter.ttk import *
from tkinter.font import *
from tktbl import *
from tkcalendar import *

class LoadTable():
    def __init__( self, username, password ):
        self.username = username
        self.password = password

    #загрузка таблицы в файл при старте
    def import_table( self, mode, l_torg=None, r_torg=None, f_name=None, l_quot=None, r_quot=None ):
        if os.path.exists('C:\\temp\\out.csv'):
            os.remove('C:\\temp\\out.csv')
        get_table = mysql.connector.connect( host = 'localhost',
                                             database = 'fut_cen_bum',
                                             user = self.username,
                                             password = self.password )
        get_table._open_connection()
        load_table = get_table.cursor()
        if mode == 'init':
            load_table.execute( 'SELECT * FROM f_zb ' 
			        'INTO OUTFILE \'C:/temp/out.csv\' '
			        'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' '
			        'LINES TERMINATED BY \'\n\';' )
        elif mode == 'filtering':
            if f_name == '-не выбрано-':
                load_table.execute( 'SELECT * FROM f_zb '
                                    'WHERE torg_date BETWEEN CAST(\'' + l_torg + '\' AS DATE) ' +
                                                        'AND CAST(\'' + r_torg + '\' AS DATE) ' +
                                    'AND QUOTATION BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
                                    'INTO OUTFILE \'C:/temp/out.csv\' ' +
                                    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                                    'LINES TERMINATED BY \'\n\';' )

            else:
                load_table.execute( 'SELECT * FROM f_zb '
                                    'WHERE torg_date BETWEEN CAST(\'' + l_torg + '\' AS DATE) ' +
                                                        'AND CAST(\'' + r_torg + '\' AS DATE) ' +
                                    'AND name=\'' + f_name + '\' ' +
                                    'AND QUOTATION BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
                                    'INTO OUTFILE \'C:/temp/out.csv\' ' +
                                    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
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

class TableWnd:
    def __init__( self, master, username, password ):
    #атрибуты
        self.master = master
        self.username = username
        self.password = password
    #параметры окна
        self.table_wnd = Toplevel( self.master )
        self.table_wnd.geometry( '1006x445+160+140' )
        self.table_wnd.title( 'Фьючерсы' )
        self.table_wnd.resizable( width=False, height=False )
        self.tableframe = Frame( self.table_wnd, width=700, height=445 )
        self.tableframe.place( x=10, y=10 )
        self.get_filters_values()
    #работа с таблицей
        self.tablemodel = MyTableModel( rows=2000, columns=7 )
        self.table = MyTableCanvas( self.tableframe, self.tablemodel,
                                    cols=7, height=395, width=700,
                                    cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                    rowselectedcolor='blue', editable=True )
        self.main_table = LoadTable( self.username, self.password )
        self.main_table.import_table( 'init' )
        self.table.adjustColumnWidths()
        self.table.importCSV( 'C:\\temp\\out.csv' )
        self.table.show()
    #главное меню
        self.main_menu = Menu( self.table_wnd )
        self.table_wnd.config( menu=self.main_menu )
        self.main_menu.add_command( label='Основные показатели', command=self.log_on )
        self.main_menu.add_command( label='Статистические характеристики', command=self.stat_on )
        self.main_menu.add_command( label='Проверка нормальности', command=self.norm_on )
        self.main_menu.add_command( label='Помощь', command=self.help_on )
    #фрейм "Фильтрация"
        self.filters_label = Label( self.table_wnd, text='Фильтрация', font='TkDefaultFont 12 bold', width=11 )
        self.filters_frame = LabelFrame( self.table_wnd, width=210, height=270, labelwidget=self.filters_label, labelanchor='n', text='Фильтрация')
        self.filters_frame.place( x=785, y=10 )
    #второй фрейм
        self.lower_frame = LabelFrame( self.table_wnd, width=210, height=155 )
        self.lower_frame.place( x=785, y=280 )
    #надпись "Диапазон по дате торгов"
        self.torg_date_label = Label( self.table_wnd, text='Диапазон по дате торгов', font='TkDefaultFont 9 underline', width=24 )
        self.torg_date_label.place( x=803, y=40 )
    #надпись "По имени фьючерса"
        self.name_label = Label( self.table_wnd, text='По имени фьючерса', font='TkDefaultFon, 9 underline', width=24 )
        self.name_label.place( x=803, y=92 )
    #надпись "Диапазон по котировке"
        self.quot_label = Label( self.table_wnd, text='Диапазон по тек. цене', font='TkDefaultFont 9 underline', width=24 )
        self.quot_label.place( x=803, y=144 )
    #левая граница даты
        self.torg_date_from = DateEntry( self.table_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                         firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                         maxdate=self.maxdate, year=self.mindate.year, month=self.mindate.month,
                                         day=self.mindate.day, showweeknumbers=False, style='entry_style.DateEntry' )
        self.torg_date_from.config( state='readonly', disableddaybackground='grey35',
                                                      disableddayforeground='grey50' ,
                                                      weekendbackground='firebrick1',
                                                      weekendforeground='brown4',
                                                      othermonthbackground='grey75',
                                                      othermonthforeground='grey25',
                                                      othermonthwebackground='firebrick4',
                                                      othermonthweforeground='black' )
        self.torg_date_from.place( x=803, y=62 )
    #правая граница даты
        self.torg_date_to = DateEntry( self.table_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                       firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                       maxdate=self.maxdate, showweeknumbers=False, style='date_style.DateEntry' )
        self.torg_date_to.config( state='readonly', disableddaybackground='grey35',
                                                    disableddayforeground='grey50',
                                                    weekendbackground='firebrick1',
                                                    weekendforeground='brown4',
                                                    othermonthbackground='grey75',
                                                    othermonthforeground='grey25',
                                                    othermonthwebackground='firebrick4',
                                                    othermonthweforeground='black' )
        self.torg_date_to.place( x=891, y=62 )
    #ограничения по выбору дат в календарях, если уже выбрана она из дат
        self.torg_date_from.bind( '<<DateEntrySelected>>', self.from_date_sel )
        self.torg_date_to.bind( '<<DateEntrySelected>>', self.to_date_sel )
    #список с выбором имени фьючерса
        self.name_menu = Combobox( self.table_wnd, state="readonly", font='TkDefaultFont 10 bold' )
        self.name_menu['values'] = tuple( self.fut_names )
        self.name_menu.current(0)
        self.name_menu.place( x=803, y=114, width=176 )
    #текстовое поле для ввода левой границы котировки
        self.quot_from = Entry( self.table_wnd, width=12, style='entry_style.TEntry', font='TkDefaultFont 10 bold' )
        self.quot_from.insert( 0, self.filterquot[0] )
        self.quot_from.place( x=803, y=166 )
    #текстовое поле для ввода правой границы котировки
        self.quot_to = Entry( self.table_wnd, width=12, style='entry_style.TEntry', font='TkDefaultFont 10 bold' )
        self.quot_to.insert( 0, self.filterquot[1] )
        self.quot_to.place( x=891, y=166 )
    #кнопка "Применить фильтры"
        self.append = Button( self.table_wnd, text='Применить фильтры', width=22, command=self.append_on )
        self.append.place( x=818, y=210 )
    #кнопка "Сбросить фильтры"
        self.clear = Button( self.table_wnd, text='Сбросить фильтры', width=22, command=self.clear_on )
        self.clear.place( x=818, y=240 )
    #кнопка "Сохранить изменения"
        self.save = Button( self.table_wnd, text='Сохранить изменения', width=22, command=self.save_on )
        self.save.place( x=818, y=300 )
    #кнопка "Откатить изменения"
        self.undo = Button( self.table_wnd, text='Откатить изменения', width=22, command=self.undo_on )
        self.undo.place( x=818, y=330 )    
    #обработка закрытия окна
        self.table_wnd.protocol( 'WM_DELETE_WINDOW', self.table_wnd_close )

   #загрузка параметров фильтра
    def get_filters_values(self):
        if os.path.exists('C:\\temp\\maxmin.csv'):
            os.remove('C:\\temp\\maxmin.csv')
        if os.path.exists('C:\\temp\\fnames.csv'):
            os.remove('C:\\temp\\fnames.csv')
        get_filter = mysql.connector.connect( host = 'localhost',
                                              database = 'fut_cen_bum',
                                              user = self.username,
                                              password = self.password )
        load_filter = get_filter.cursor()
        load_filter.execute( 'SELECT MIN(torg_date), MIN(quotation), MAX(torg_date), MAX(quotation) '+
                             'FROM f_zb INTO OUTFILE \'C:/temp/maxmin.csv\' '+
                             'FIELDS ENCLOSED BY \'"\' TERMINATED BY \'\n\' LINES TERMINATED BY \'\n\';' )
        load_filter.execute( 'SELECT DISTINCT name FROM f_zb INTO OUTFILE \'C:/temp/fnames.csv\' '+
                             'FIELDS ENCLOSED BY \'"\' TERMINATED BY \'\n\' LINES TERMINATED BY \'\n\';' )
        load_filter.close()
        get_filter.close()
        self.filterdates = []
        self.filterquot = []
        self.fut_names = ['-не выбрано-']
        with open( 'C:\\temp\\maxmin.csv', 'r+', newline='' ) as maxminfile:
            date_quot_read = csv.reader( maxminfile, quotechar='"' )
            date_quot_read = list( date_quot_read )
            self.filterdates = [ ''.join( date_quot_read[0] ), ''.join( date_quot_read[2] ) ]
            self.filterquot = [ ''.join( date_quot_read[1] ), ''.join( date_quot_read[3] ) ]
        with open( 'C:\\temp\\fnames.csv', 'r+', newline='' ) as fnamesfile:
            fnames_read = csv.reader( fnamesfile, quotechar='"' )
            for row in fnames_read:
                self.fut_names += row
    #крайние даты для фильтрования
        self.mindate = datetime.date.fromisoformat( self.filterdates[0] )
        self.maxdate = datetime.date.fromisoformat( self.filterdates[1] )

    #функции, ограничивающие выбор даты 
    def from_date_sel( self, event ):
        self.torg_date_to.config( mindate=self.torg_date_from.get_date() )
    def to_date_sel( self, event ):
        self.torg_date_from.config( maxdate=self.torg_date_to.get_date() )

    #кнопка "Применить фильтры"
    def append_on(self):               
        l_date = self.torg_date_from.get()
        r_date = self.torg_date_to.get()
        f_name = self.name_menu.get()
        l_quot = self.quot_from.get()
        r_quot = self.quot_to.get()
        if not self.quot_check( l_quot ) or not self.quot_check( r_quot ):
            messagebox.showerror( 'Ошибка', 'Неправильно введена котировка!' )
        else:
            l_quot = l_quot.replace( ',','.' )
            r_quot = r_quot.replace( ',','.' )
            if float( l_quot ) > float( r_quot ):
                messagebox.showerror( 'Ошибка', 'Неправильно введена котировка!' )
            if float( l_quot ) < float( self.filterquot[0] ):
                self.quot_from.delete( 0, END )
                self.quot_from.insert( 0, self.filterquot[0] )
                l_quot = self.filterquot[0]
            elif float( r_quot ) > float( self.filterquot[1] ):
                self.quot_to.delete( 0, END )
                self.quot_to.insert( 0, self.filterquot[1] )
                r_quot = self.filterquot[1]
            self.main_table.import_table( 'filtering', l_date, r_date, f_name, l_quot, r_quot )
            self.table.adjustColumnWidths()
            self.table.importCSV( 'C:\\temp\\out.csv' )
            self.table.show()

    #проверка quotation
    def quot_check( self, quot ):
        flag_dot = 0
        if quot=='': return False
        for symb in quot:                         #поиск недопустимых символов
            if symb.isnumeric() == True: pass
            elif symb == '.' or symb == ',':
                flag_dot += 1                     #обнаружена одна запятая или точка, больше их уже быть не может
            elif flag_dot > 1:                      #если найдена еще одна точка (такого быть не может)
                return False
            else: return False
        quot = quot.replace( ',', '.' )
        if float( quot ) < 0: return False
        if ( len( quot ) > 1 and quot[0] == '0' and quot[1] != '.' or    #если число начинается на 0, но не 0.
             len( quot ) == 2 and quot[1] == '.'):                       #если последний символ - .
               return False   
        return True

    #кнопка "Сбросить фильтры"
    def clear_on(self):
        self.torg_date_from.set_date( self.mindate ) 
        self.torg_date_to.set_date( self.maxdate )
        self.name_menu.current(0)
        self.quot_from.delete( 0, END )
        self.quot_from.insert( 0, self.filterquot[0] )                    
        self.quot_to.delete( 0, END )
        self.quot_to.insert( 0, self.filterquot[1] )

    #кнопка "Сохранить изменения"
    def save_on(self):
        save = messagebox.askyesno( title = 'Сохранение изменений',
                                    message = 'Изменить базу данных?' )
        if save:
            if self.table.del_records != []:
                for delrow in self.table.del_records:
                    edit_db = mysql.connector.connect( host = 'localhost',
                                                       database = 'fut_cen_bum',
                                                       user = self.username,
                                                       password = self.password )
                    edit_db._open_connection()
                    edit_db_cursor = edit_db.cursor()
                    edit_db_cursor.execute( 'DELETE FROM f_zb WHERE ' +
                                            'torg_date=CAST(\'' + str(delrow[0]) + '\' AS DATE) AND ' +
                                            'name=\''+str(delrow[1])+'\' AND '+
                                            'day_end=CAST(\'' + str(delrow[2]) + '\' AS DATE) AND ' +
                                            'quotation=' + str(delrow[3]) + ' AND ' +
                                            'min_quot=' + str(delrow[4]) + ' AND ' +
                                            'max_quot=' + str(delrow[5]) + ' AND ' +
                                            'num_contr=' + str(delrow[6]) + ';' )
                    edit_db_cursor.close()
                    edit_db.close()
                messagebox.showinfo( title = 'Изменение БД',
                                     message = 'База данных успешно изменена!' )
                self.get_filters_values()
                self.torg_date_from.config( maxdate = self.maxdate, mindate = self.mindate )
                self.torg_date_to.config( maxdate = self.maxdate, mindate = self.mindate )
                if self.torg_date_from.get_date() < self.mindate:
                    self.torg_date_from.set_date( self.mindate.year )
                if self.torg_date_to.get_date() > self.maxdate:
                    self.torg_date_from.config( self.mindate.year )
                if self.quot_from.get() < self.filterquot[0]:
                    self.quot_from.delete( 0, END )
                    self.quot_from.insert( 0, self.filterquot[0] )
                if self.quot_to.get() > self.filterquot[1]:
                    self.quot_to.delete( 0, END )
                    self.quot_to.insert( 0, self.filterquot[1] )
                if self.quot_to.get() < self.quot_from.get():
                    self.quot_from.delete( 0, END )
                    self.quot_from.insert( 0, self.filterquot[0] )
                    print(self.filterquot[0]) 
                self.name_menu['values'] = tuple( self.fut_names )
                self.name_menu.current(0)
                self.append_on()
            #for i in 
            if len(self.table.model.edit_records) != 0:
                for editrow in self.table.model.edit_records:
                    pass
                if self.table.del_records == []:
                    messagebox.showinfo( title = 'Изменение БД',
                                         message = 'База данных успешно изменена!' )
                self.get_filters_values()
                self.torg_date_from.config( maxdate = self.maxdate, mindate = self.mindate )
                self.torg_date_to.config( maxdate = self.maxdate, mindate = self.mindate )
                if self.torg_date_from.get_date() < self.mindate:
                    self.torg_date_from.set_date( self.mindate.year )
                if self.torg_date_to.get_date() > self.maxdate:
                    self.torg_date_from.config( self.mindate.year )
                if self.quot_from.get() < self.filterquot[0]:
                    self.quot_from.delete( 0, END )
                    self.quot_from.insert( 0, self.filterquot[0] )
                if self.quot_to.get() > self.filterquot[1]:
                    self.quot_to.delete( 0, END )
                    self.quot_to.insert( 0, self.filterquot[1] )
                if self.quot_to.get() < self.quot_from.get():
                    self.quot_from.delete( 0, END )
                    self.quot_from.insert( 0, self.filterquot[0] )
                    print(self.filterquot[0]) 
                self.name_menu['values'] = tuple( self.fut_names )
                self.name_menu.current(0)
                self.append_on()
            self.table.del_records.clear()
            self.table.model.edit_records.clear()
            
    #кнопка "Откатить изменения"
    def undo_on(self):
        undo = messagebox.askyesno( title = 'Отмена изменений',
                                    message = 'Откатить все изменения?' )
        if undo:
            self.table.del_records.clear()
            self.table.model.edit_records.clear()
            self.append_on()

    #запрос подтверждения выхода при несохраненной инф-ии
    def table_wnd_close(self):
        if self.table.del_records != []:
            not_saved = messagebox.askyesno( title = 'Выход',
                                             message = 'Вы действительно хотите выйти?\n'+
                                                       'Несохраненные данные будут потеряны!' )
            if not_saved:
                self.master.destroy()
        else:
            self.master.destroy()

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
    username = ''
    password = ''
    def __init__(self):
    #создание окна с запросом пароля и логина
        self.master = Tk()
    #пользовательский стиль записей и выпадающих списков
        self.entry_style = Style()
        self.entry_style.configure( 'TEntry', foreground='blue' )
        self.date_style= Style()
        self.date_style.configure( 'DateEntry', foreground='blue' )
        self.combo_style = Style()
        self.combo_style.configure( 'TCombobox', foreground='blue' )
        self.master.option_add( '*TCombobox*Listbox.font', 'TkDefaultFont 10 bold' )
        self.master.option_add( '*TCombobox*Listbox.foreground', 'blue' )
    #параметры окна
        self.master.resizable( width=False, height=False )
        self.master.geometry( '280x130+530+300' )
        self.master.title( 'Авторизация' )
        self.master.resizable( width=False, height=False )
    #пояснение к окну
        self.loginpswd_label = Label( self.master,
                                      text='Введите логин и пароль от сервера MySQL:',
                                      font='TkDefaultFont 9', width=40 )
        self.loginpswd_label.place( x=16, y=5 )
    #ввод логина
        self.login_label = Label( self.master, text='Логин:', font=('TkDefaultFont', 9, 'underline'), width=7 )
        self.login_label.place( x=10, y=30 )
        self.login_entry = Entry( self.master, width=24, style='entry_style.TEntry', font='Courier 10 bold' )
        self.login_entry.place( x=65, y=30 )
        self.login_entry.insert( 0, 'root' )
    #ввод пароля
        self.password_label = Label( self.master, text='Пароль:', font='TkDefaultFont 9 underline', width=7 )
        self.password_label.place( x=10, y=60 )
        self.password_entry = Entry( self.master, width=24, style='entry_style.TEntry', font='Courier 10 bold' )
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
            check_login_pswd.close()
        except mysql.connector.Error:
            messagebox.showerror('Ошибка', 'Неправильный логин или пароль!')
        else:
            self.username = login
            self.password = pswrd
            self.master.withdraw()
            self.table_window = TableWnd( self.master, self.username, self.password )

def main():   
    root = MainWnd()

if __name__ == "__main__":
    main()
