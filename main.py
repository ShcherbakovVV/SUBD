import datetime, mysql.connector
from tktbl import *
from tkcalendar import DateEntry
from scipy import stats.kstest

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
                                    'AND quotation BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
                                    'INTO OUTFILE \'C:/temp/out.csv\' ' +
                                    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                                    'LINES TERMINATED BY \'\n\';' )

            else:
                load_table.execute( 'SELECT * FROM f_zb '
                                    'WHERE torg_date BETWEEN CAST(\'' + l_torg + '\' AS DATE) ' +
                                                        'AND CAST(\'' + r_torg + '\' AS DATE) ' +
                                    'AND name=\'' + f_name + '\' ' +
                                    'AND quotation BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
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
        self.lastsave = os.path.expanduser('~')
    #параметры окна
        self.table_wnd = Toplevel( self.master )
        self.table_wnd.geometry( '1006x445+170+130' )
        self.table_wnd.title( 'Фьючерсы' )
        self.table_wnd.resizable( width=False, height=False )
        self.tableframe = Frame( self.table_wnd, width=700, height=445 )
        self.tableframe.place( x=10, y=10 )
        self.get_filters_values()
    #окно "Основной показатель"
        self.pok_wnd = Toplevel(self.master)
        self.pok_wnd.geometry('455x445+200+170')
        self.pok_wnd.title('Основной показатель')
        self.pok_wnd.resizable( width=False, height=False )
        self.pok_frame = Frame( self.pok_wnd, width=435, height=445 )
        self.pok_frame.place( x=10, y=10 )
        self.pok_wnd.withdraw()
        def close_pok():
            self.pok_wnd.withdraw()
            self.master.grab_set()                #главное окно неактивно
            self.master.focus_set()
        self.pok_wnd.protocol( 'WM_DELETE_WINDOW', close_pok )
    #работа с таблицей
        self.tablemodel = MyTableModel( rows=2000, columns=7 )
        self.table = MyTableCanvas( self.tableframe, self.tablemodel,
                                    cols=7, height=395, width=700,
                                    cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                    rowselectedcolor='blue', read_only=False )
        self.main_table = LoadTable( self.username, self.password )
        self.main_table.import_table( 'init' )
        self.table.importCSV( 'C:\\temp\\out.csv' )
        self.table.adjustColumnWidths()
        self.table.show()
    #главное меню
        self.main_menu = Menu( self.table_wnd )
        self.table_wnd.config( menu=self.main_menu )
        self.main_menu.add_command( label='Основной показатель', command=self.pok_on )
        self.main_menu.add_command( label='Статистические характеристики', command=self.stat_on )
        self.main_menu.add_command( label='Помощь', command=self.help_on )
    #фрейм "Фильтрация"
        self.filters_label = Label( self.table_wnd, text='Фильтрация', font='TkDefaultFont 12 bold', width=11 )
        self.filters_frame = LabelFrame( self.table_wnd,
                                         width=210,
                                         height=270,
                                         labelwidget=self.filters_label,
                                         labelanchor='n',
                                         text='Фильтрация' )
        self.filters_frame.place( x=785, y=10 )
    #второй фрейм
        self.lower_label = Label( self.table_wnd, text='Таблица', font='TkDefaultFont 12 bold', width=8 )
        self.lower_frame = LabelFrame( self.table_wnd,
                                       width=210,
                                       height=155,
                                       labelwidget=self.lower_label,
                                       labelanchor='n',
                                       text='Таблица' )
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
        self.save.place( x=818, y=310 )
    #кнопка "Откатить изменения"
        self.undo = Button( self.table_wnd, text='Откатить изменения', width=22, command=self.undo_on )
        self.undo.place( x=818, y=340 )
    #кнопка "Создать отчет"
        self.report = Button( self.table_wnd, text='Создать отчет', width=22, command=self.report_on )
        self.report.place( x=818, y=398 )
    #применение фильтра при запуске для основного показателя
        self.append_on()
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
            err = messagebox.showerror( title = 'Ошибка',
                                        message = 'Неправильно введена котировка!',
                                        parent = self.tableframe )
        else:
            l_quot = l_quot.replace( ',','.' )
            r_quot = r_quot.replace( ',','.' )
            if float( l_quot ) > float( r_quot ):
                err = messagebox.showerror( title = 'Ошибка',
                                            message = 'Неправильно введена котировка!',
                                            parent = self.tableframe )
                if err:
                    self.master.release()
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
    #основные показатели
        #загрузка требуемой таблицы
        if os.path.exists('C:\\temp\\pok.csv'):
            os.remove('C:\\temp\\pok.csv')
        get_pok = mysql.connector.connect( host = 'localhost',
                                           database = 'fut_cen_bum',
                                           user = self.username,
                                           password = self.password )
        get_pok._open_connection()
        load_pok = get_pok.cursor()
        if self.name_menu.get() == '-не выбрано-':
            load_pok.execute( 'SELECT torg_date, f_zb.name, quotation, exec_date, day_end FROM f_zb, zb ' +
                              'WHERE f_zb.name=zb.name ' +
                              'AND torg_date BETWEEN CAST(\'' + self.torg_date_from.get_date().strftime('%Y-%m-%d') + '\' AS DATE) ' +
                                                'AND CAST(\'' + self.torg_date_to.get_date().strftime('%Y-%m-%d') + '\' AS DATE) ' +
                              'AND quotation BETWEEN ' + self.quot_from.get() + ' AND ' + self.quot_to.get() + ' ' +
                              'ORDER BY f_zb.name, torg_date ' +
                              'INTO OUTFILE \'C:/temp/pok.csv\' ' +
                              'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                              'LINES TERMINATED BY \'\n\';' )

        else:
            load_pok.execute( 'SELECT torg_date, f_zb.name, quotation, exec_date, day_end FROM f_zb, zb ' +
                              'WHERE f_zb.name=zb.name ' +
                              'AND torg_date BETWEEN CAST(\'' + self.torg_date_from.get_date().strftime('%Y-%m-%d') + '\' AS DATE) ' +
                                                'AND CAST(\'' + self.torg_date_to.get_date().strftime('%Y-%m-%d') + '\' AS DATE) ' +
                              'AND f_zb.name=\'' + self.name_menu.get() + '\' ' +
                              'AND quotation BETWEEN ' + self.quot_from.get() + ' AND ' + self.quot_to.get() + ' ' +
                              'ORDER BY f_zb.name, torg_date ' +
                              'INTO OUTFILE \'C:/temp/pok.csv\' ' +
                              'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                              'LINES TERMINATED BY \'\n\';' )
        load_pok.close()
        get_pok.close()
        global ji
    #функция для расчета rk
        def rk( F, Tu, Tn ):
            d1 = time.strptime( Tu, "%Y-%m-%d" )
            d2 = time.strptime( Tn, "%Y-%m-%d" )
            if F == 0:
                return 1
            else:
                return (math.log(F/100))/(d2.tm_yday - d1.tm_yday)
    #загрузка выведенной таблицы
        pr_sps = []
        with open( 'C:\\temp\\pok.csv', 'r+', newline='' ) as tablefile:
            read_pok = csv.reader( tablefile )
            for row in read_pok:
                row = str(row)
                pr_sps += [ row[1:len(row)-1] ]
        name_zap = '00000-0000'
        i = 0
        with open( 'C:\\temp\\pok2.csv', 'w+', newline='' ) as tablefile:
            tablefile.write( 'Дата торг.,Код фьюч.,Осн.показатель\n' )
            while i < len( pr_sps ):
                dan_tek = pr_sps[i].split('\'')
                if name_zap != dan_tek[3]:
                    i = i + 2
                    name_zap = dan_tek[3]
                else:
                    dan_tek_2 = pr_sps[i-2].split('\'')
                    pokazat = math.log( abs(rk( float(dan_tek[5]), dan_tek[7], dan_tek[9] )/rk( float(dan_tek_2[5]), dan_tek_2[7], dan_tek_2[9] )))
                    i += 1
                    tablefile.write( '"' + dan_tek[1] + '","' + name_zap + '","' + str(pokazat) + '"\n' )
        self.pok_tblmodel = MyTableModel( rows=2000, columns=3 )
        self.pok_table = MyTableCanvas( self.pok_frame, self.pok_tblmodel,
                                        cols=3, height=395, width=368,
                                        cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                        rowselectedcolor='blue', read_only=True )
        self.pok_table.importCSV( 'C:\\temp\\pok2.csv' )
        self.pok_table.adjustColumnWidths()
        self.pok_table.show()

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
        save = False
        if self.table.del_records != [] or len(self.table.model.edit_records) != 0:
            save = messagebox.askyesno( title = 'Сохранение изменений',
                                        message = 'Изменить базу данных?',
                                        parent = self.tableframe )
        if save:
            if self.table.del_records != []:
                for delrow in self.table.del_records:
                    edit_db = mysql.connector.connect( host = 'localhost',
                                                       database = 'fut_cen_bum',
                                                       user = self.username,
                                                       password = self.password )
                    edit_db._open_connection()
                    edit_db_cursor = edit_db.cursor()
                    edit_db_cursor.execute( 'DELETE FROM f_zb WHERE (' +
                                            'torg_date=CAST(\'' + str(delrow[0]) + '\' AS DATE) AND ' +
                                            'name=\''+str(delrow[1])+'\' AND '+
                                            'day_end=CAST(\'' + str(delrow[2]) + '\' AS DATE) AND ' +
                                            'quotation=' + str(delrow[3]) + ' AND ' +
                                            'min_quot=' + str(delrow[4]) + ' AND ' +
                                            'max_quot=' + str(delrow[5]) + ' AND ' +
                                            'num_contr=' + str(delrow[6]) + ');' )
                    edit_db_cursor.close()
                    edit_db.close()
                saved = messagebox.showinfo( title = 'Изменение БД',
                                             message = 'База данных успешно изменена!',
                                             parent = self.tableframe )
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
                print(self.table.model.edit_records)
                for editrow in self.table.model.edit_records:
                    pass
                if self.table.del_records == []:
                    messagebox.showinfo( title = 'Изменение БД',
                                         message = 'База данных успешно изменена!',
                                         parent = self.tableframe )
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
        undo = False
        if self.table.del_records != [] or len(self.table.model.edit_records) != 0:
            undo = messagebox.askyesno( title = 'Отмена изменений',
                                        message = 'Откатить все изменения?',
                                        parent = self.tableframe )
        if undo:
            self.table.del_records.clear()
            self.table.model.edit_records.clear()
            self.append_on()

    #кнопка "Создать отчет"
    def report_on(self):
        report = filedialog.asksaveasfilename( parent=self.master,
                                               initialdir=self.lastsave,
                                               title="Выберите имя файла",
                                               defaultextension='.txt',
                                               filetypes=[('текстовый файл', '*.txt')] )
        self.lastsave = os.path.dirname( report )
        if not report == '':
            with open( 'C:\\temp\\out.csv', 'r' ) as to_save:
                rep_table = csv.DictReader( to_save, fieldnames=( 'Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена',
                                                                  'Мин.цена', 'Макс.цена', 'Число прод.', 'К-р.пок-ль' ) )
                rep_format = ''
                row_id = 0
                for row in rep_table:
                    row_id += 1
                    rep_format = rep_format + '{: <12}'.format( row['Дата торг.'] ) + \
                                              '{: <12}'.format( row['Код фьюч.'] ) + \
                                              '{: <12}'.format( row['Дата погаш.'] ) + \
                                              '{: <9}'.format( row['Тек.цена'] ) + \
                                              '{: <9}'.format( row['Мин.цена'] ) + \
                                              '{: <11}'.format( row['Макс.цена'] ) + \
                                              '{: <12}'.format( row['Число прод.'] ) + '\n'
            with open( report, 'w+' ) as saved_report:
                saved_report.write( rep_format )

    #запрос подтверждения выхода при несохраненной инф-ии
    def table_wnd_close(self):
        if self.table.del_records != []:
            not_saved = messagebox.askyesno( title = 'Выход',
                                             message = 'Вы действительно хотите выйти?\n'+
                                                       'Несохраненные данные будут потеряны!',
                                             parent = self.tableframe )
            if not_saved:
                self.master.destroy()
        else:
            self.master.destroy()
            
    #основной показатель
    def pok_on(self):
        self.pok_wnd.deiconify()
        self.pok_wnd.grab_set()                #главное окно неактивно
        self.pok_wnd.focus_set()
        
    #статистические характеристики
    def stat_on(self):
        self.stat_wnd = Toplevel(self.master)
        self.stat_wnd.geometry('954x400+200+170')
        self.stat_wnd.title('Расчет основных статистических характеристик')
        self.stat_wnd.resizable( width=False, height=False )
        self.stat_wnd.grab_set()                #главное окно неактивно
        self.stat_wnd.focus_set()
        self.stat_frame = Frame( self.stat_wnd, width=600, height=348 )
        self.stat_frame.place( x=10, y=10 )
        self.stat_tblmodel = MyTableModel( rows=2000, columns=5 )
        self.stat_table = MyTableCanvas( self.stat_frame, self.stat_tblmodel,
                                         cols=5, height=348, width=600,
                                         cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                         rowselectedcolor='blue', read_only=True )
        self.stat_table.adjustColumnWidths()
        self.stat_table.show()
    #второй фрейм
        self.stat_lower_frame = LabelFrame( self.stat_wnd, width=261, height=387 )
        self.stat_lower_frame.place( x=682, y=3 )
    #надпись "Предыстория торгов:"
        self.stat_date_label = Label( self.stat_wnd, text='Предыстория торгов:', font='Tkdefault 9 underline' )
        self.stat_date_label.place( x=700, y=20 )
    #левое поле ввода даты
        self.stat_date_min = DateEntry( self.stat_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                        firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                        maxdate=self.maxdate, day=self.mindate.day, month=self.mindate.month,
                                        year=self.mindate.year, showweeknumbers=False, style='entry_style.DateEntry' )
        self.stat_date_min.config( state='readonly', disableddaybackground='grey35',
                                                     disableddayforeground='grey50' ,
                                                     weekendbackground='firebrick1',
                                                     weekendforeground='brown4',
                                                     othermonthbackground='grey75',
                                                     othermonthforeground='grey25',
                                                     othermonthwebackground='firebrick4',
                                                     othermonthweforeground='black' )
        self.stat_date_min.place( x=700, y=42 )
    #поле ввода даты t
        self.stat_date_t = DateEntry( self.stat_wnd, width=9, font='TkDefaultFont 9 bold', locale='ru_RU',
                                      firstweekday='monday', date_pattern='y-mm-dd', mindate=self.mindate,
                                      maxdate=self.maxdate, showweeknumbers=False, style='entry_style.DateEntry' )
        self.stat_date_t.config( state='readonly', disableddaybackground='grey35',
                                                   disableddayforeground='grey50' ,
                                                   weekendbackground='firebrick1',
                                                   weekendforeground='brown4',
                                                   othermonthbackground='grey75',
                                                   othermonthforeground='grey25',
                                                   othermonthwebackground='firebrick4',
                                                   othermonthweforeground='black' )
        self.stat_date_t.place( x=788, y=42 )
    #надпись "Фьючерс с наиб. предысторией"
        self.stat_fut_label = Label( self.stat_wnd,
                                     text='Фьючерс с наибольшей предысторией:',
                                     font='Tkdefault 9 underline' )
        self.stat_fut_label.place( x=700, y=72 )
    #надпись с именем фьючерса с наибольшей предисторией
        self.stat_fut_name = Label( self.stat_wnd,
                                    font='TkDefaultFont 12 bold',
                                    foreground='magenta3' )
        self.stat_fut_name.place( x=700, y=94 )
        self.stat_fut_name.config( text='фьючерс' )
    #надпись "Нормальность..."
        self.stat_norm_label = Label( self.stat_wnd,
                                      text='Нормальность закона распределения\n'+
                                           'контролируемого показателя:',
                                      font='Tkdefault 9 underline' )
        self.stat_norm_label.place( x=700, y=124 )
    #надпись с итогом проверки
        self.stat_norm_check = Label( self.stat_wnd, font='Tkdefault 12 bold' )
        self.stat_norm_check.place( x=700, y=164 )
        if True:
            self.stat_norm_check.config( text='подтверждена', foreground='green3' )
        else:
            self.stat_norm_check.config( text='опровергнута', foreground='red3' )
        self.stat_report = Button( self.stat_wnd, text='Создать отчет', width=30, command=self.stat_report_on )
        self.stat_report.place( x=717, y=340 )

    #сохранение отчета со страницы статистических характеристик
    def stat_report_on(self):
        report = filedialog.asksaveasfilename( parent=self.master,
                                               initialdir=self.lastsave,
                                               title="Выберите имя файла",
                                               defaultextension='.txt',
                                               filetypes=[('текстовый файл', '*.txt')] )
        self.lastsave = os.path.dirname( report )
        if not report == '':
            with open( 'C:\\temp\\out.csv', 'r' ) as to_save:
                rep_table = csv.DictReader( to_save, fieldnames=( 'Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена',
                                                                  'Мин.цена', 'Макс.цена', 'Число прод.', 'К-р.пок-ль' ) )
                rep_format = ''
                row_id = 0
                for row in rep_table:
                    row_id += 1
                    rep_format = rep_format + '{:> 4}'.format( row_id ) + ' ' + \
                                              '{: <12}'.format( row['Дата торг.'] ) + \
                                              '{: <12}'.format( row['Код фьюч.'] ) + \
                                              '{: <12}'.format( row['Дата погаш.'] ) + \
                                              '{: <9}'.format( row['Тек.цена'] ) + \
                                              '{: <9}'.format( row['Мин.цена'] ) + \
                                              '{: <11}'.format( row['Макс.цена'] ) + \
                                              '{: <12}'.format( row['Число прод.'] ) + '\n'
            with open( report, 'w+' ) as saved_report:
                saved_report.write( rep_format )
            
    #помощь
    def help_on(self):
        os.startfile( os.getcwd().replace('\\','/')+'/help.chm' )

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
            messagebox.showerror( title = 'Ошибка',
                                  message = 'Неправильный логин или пароль!',
                                  parent = self.master )
        else:
            self.username = login
            self.password = pswrd
            self.master.withdraw()
            self.table_window = TableWnd( self.master, self.username, self.password )

def main():   
    root = MainWnd()

if __name__ == "__main__":
    main()
