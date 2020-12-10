import mysql.connector
from datetime import date
from tktbl import *
from tkcalendar import DateEntry
from scipy.stats import chisquare
from xlsxwriter import Workbook

#окно "статистические характеристики"
class StatWnd:
    def __init__(self, master, username, password, mindate, maxdate):
        self.master = master
        self.username = username
        self.password = password
        self.mindate = mindate
        self.maxdate = maxdate
        self.lastsave = os.path.expanduser('~')
        self.stat_wnd = Toplevel( self.master )
        self.stat_wnd.geometry('854x400+250+170')
        self.stat_wnd.title('Расчет основных статистических характеристик')
        self.stat_wnd.resizable( width=False, height=False )
        self.stat_wnd.grab_set()                #главное окно неактивно
        self.stat_wnd.focus_set()
        self.stat_frame = Frame( self.stat_wnd, width=500, height=348 )
        self.stat_frame.place( x=10, y=10 )
    #построение таблицы
        self.stat_tblmodel = MyTableModel( rows=2000, columns=5 )
        self.stat_table = MyTableCanvas( self.stat_frame, self.stat_tblmodel,
                                         cols=5, height=348, width=500,
                                         cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                         rowselectedcolor='blue', read_only=True )
    #второй фрейм
        self.stat_lower_frame = LabelFrame( self.stat_wnd, width=261, height=387 )
        self.stat_lower_frame.place( x=582, y=3 )
    #надпись "Предыстория торгов:"
        self.stat_date_label = Label( self.stat_wnd, text='Предыстория торгов:', font='Tkdefault 9 underline' )
        self.stat_date_label.place( x=600, y=20 )
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
        self.stat_date_min.place( x=609, y=42 )
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
        self.stat_date_t.place( x=728, y=42 )
    #считываем заданное в фильтрах значение
        self.stat_filt_date_min = self.stat_date_min.get_date()
        self.stat_filt_date_t = self.stat_date_t.get_date()
    #задание интервала дат
        self.stat_set_dates()
    #кнопка "Задать предысторию"
        self.stat_date_but = Button( self.stat_wnd, text='Задать предысторию', width=30, command=self.stat_refresh )
        self.stat_date_but.place( x=617, y=70 )
    #надпись "Фьючерс с наиб. предысторией"
        self.stat_fut_label = Label( self.stat_wnd,
                                     text='Фьючерс с наибольшей предысторией:',
                                     font='Tkdefault 9 underline' )
        self.stat_fut_label.place( x=600, y=106 )
    #надпись с именем фьючерса с наибольшей предисторией
        self.stat_fut_name = Label( self.stat_wnd,
                                    font='TkDefaultFont 12 bold',
                                    foreground='magenta3' )
        self.stat_fut_name.place( x=600, y=128 )
    #надпись "Нормальность..."
        self.stat_norm_label = Label( self.stat_wnd,
                                      text='Нормальность закона распределения\n'+
                                           'контролируемого показателя:',
                                      font='Tkdefault 9 underline' )
        self.stat_norm_label.place( x=600, y=152 )
    #надпись с итогом проверки
        self.stat_norm_check = Label( self.stat_wnd, font='Tkdefault 12 bold' )
        self.stat_norm_check.place( x=600, y=192 )
    #надпись "Значение довер. вероятности"
        self.stat_prob = Label( self.stat_wnd,
                                text='Значение довер. вероятности p = 0.05',
                                font='Tkdefault 9 underline' )
        self.stat_prob.place( x=600, y=220 )
    #надпись "Значение Хи-квадрат"
        self.stat_chi_label = Label( self.stat_wnd,
                                     text='Значение Хи-квадрат:',
                                     font='Tkdefault 9 underline' )
        self.stat_chi_label.place( x=600, y=240 )
    #значение Хи-квадрат
        self.stat_chi_value = Label( self.stat_wnd,
                                     font='Tkdefault 12 bold',
                                     foreground='blue2' )
        self.stat_chi_value.place( x=730, y=240 )
    #проверка нормальности
        self.stat_normality()
    #создание отчета
        self.stat_report = Button( self.stat_wnd, text='Создать отчет', width=30, command=self.stat_report_on )
        self.stat_report.place( x=617, y=340 )

    #обновление информации
    def stat_refresh(self):
        self.stat_set_dates()
        self.stat_normality()
        self.stat_filt_date_min = self.stat_date_min.get_date()
        self.stat_filt_date_t = self.stat_date_t.get_date()
        
    #задание диапазона дат
    def stat_set_dates(self):
        if os.path.exists('C:\\temp\\stat.csv'):
            os.remove('C:\\temp\\stat.csv')
        get_stat = mysql.connector.connect( host = 'localhost',
                                            database = 'fut_cen_bum',
                                            user = self.username,
                                            password = self.password )
        load_stat = get_stat.cursor()
        load_stat.execute( 'CALL stat(\'' + self.stat_date_min.get_date().strftime( "%Y-%m-%d" ) +
                                 '\', \'' + self.stat_date_t.get_date().strftime( "%Y-%m-%d" ) + '\');' )
        load_stat.close()
        get_stat.close()
    #переименовать заголовки
        with open( 'C:\\temp\\stat.csv', 'r+', newline='' ) as statfile:
            add_stat_headers = csv.reader( statfile )
            stat_headers = 'Код фьюч.,Мат.ожид.,Сркв.откл.,Минимум,Максимум\n'
            for row in add_stat_headers:
                stat_headers += ','.join(row) + '\n'
        with open( 'C:\\temp\\stat.csv', 'w+', newline = '' ) as statfile:
            statfile.write( stat_headers )
        self.stat_table.importCSV( 'C:\\temp\\stat.csv' )
        self.stat_table.adjustColumnWidths()
        self.stat_table.show()

    #проверка на нормальность
    def stat_normality(self):
        if os.path.exists('C:\\temp\\norm.csv'):
            os.remove('C:\\temp\\norm.csv')
        get_norm = mysql.connector.connect( host = 'localhost',
                                            database = 'fut_cen_bum',
                                            user = self.username,
                                            password = self.password )
        load_norm = get_norm.cursor()
        load_norm.execute( 'CALL norm(\'' + self.stat_date_min.get_date().strftime( "%Y-%m-%d" ) +
                                 '\', \'' + self.stat_date_t.get_date().strftime( "%Y-%m-%d" ) + '\');' )
        load_norm.close()
        get_norm.close()        
        with open( 'C:\\temp\\norm.csv', 'r', newline='' ) as normfile:
            norm_read = csv.reader( normfile, quotechar='"' )
            norm_vyborka = []
            for row in norm_read:
                max_fut = row[0]
                norm_vyborka.append( float(row[1]) )
    #проверка нормальности
        self.chi, self.p = chisquare( norm_vyborka )
        if self.p > 0.05:
            self.stat_norm_check.config( text='подтверждена', foreground='green3' )
        else:
            self.stat_norm_check.config( text='опровергнута', foreground='red3' )
        self.stat_fut_name.config( text=max_fut )
        self.stat_chi_value.config( text=round(self.chi, 3) )
        
    #сохранение отчета со страницы статистических характеристик
    def stat_report_on(self):
        report = filedialog.asksaveasfilename( parent=self.master,
                                               initialdir=self.lastsave,
                                               title="Выберите имя файла",
                                               defaultextension='.xlsx',
                                               filetypes=[('файл электронных таблиц', '*.xlsx')] )
        if not report == '':
            self.lastsave = os.path.dirname( report )
            stat_wb = Workbook( report )
            stat_sheet = stat_wb.add_worksheet( 'Статистические характеристики' )
            stat_wb.add_format( {'align': 'center'} )
            stat_sheet.merge_range( 'A1:E1', 'Статистические характеристики', stat_wb.add_format( {'align':'center'} ) )
            stat_sheet.merge_range( 'A2:C2', 'Предыстория торгов', stat_wb.add_format( {'align':'left'} ) )
            stat_sheet.merge_range( 'A3:E3', ' ', stat_wb.add_format( {'align':'left'} ) )
            stat_sheet.set_column( 0, 0, 14 )
            stat_sheet.set_column( 1, 1, 27 )
            stat_sheet.set_column( 2, 2, 35 )
            stat_sheet.set_column( 3, 4, 12 )
            date_format = stat_wb.add_format( {'num_format': 'dd-mm-yyyy', 'align': 'left'} )
            stat_sheet.write_datetime( 'D2', self.stat_filt_date_min, date_format )
            stat_sheet.write_datetime( 'E2', self.stat_filt_date_t, date_format )
            stat_sheet.write( 'A4', 'Код фьючерса' )
            stat_sheet.write( 'B4', 'Математическое ожидание' )
            stat_sheet.write( 'C4', 'Среднеквадратическое отклонение' )
            stat_sheet.write( 'D4', 'Минимум' )
            stat_sheet.write( 'E4', 'Максимум' )
            with open( 'C:\\temp\\stat.csv', 'r' ) as to_save_stat:
                rep_table = csv.DictReader( to_save_stat,
                                            fieldnames=( 'Код фьюч', 'Мат.ожид.', 'Сркв.откл.', 'Минимум', 'Максимум' ) )
                row_id = 3
                for row in rep_table:
                    #пропускаем строчку с сокращенными названиями
                    if row_id == 3:
                        pass
                    else:
                        stat_sheet.write( row_id, 0, row['Код фьюч'] )
                        stat_sheet.write( row_id, 1, row['Мат.ожид.'] )
                        stat_sheet.write( row_id, 2, row['Сркв.откл.'] )
                        stat_sheet.write( row_id, 3, row['Минимум'] )
                        stat_sheet.write( row_id, 4, row['Максимум'] )
                    row_id += 1   
            stat_wb.close()

#класс окна с основной таблицей
class TableWnd:
    def __init__( self, master, username, password ):
    #атрибуты
        self.master = master
        self.username = username
        self.password = password
        self.lastsave = os.path.expanduser('~')
    #параметры окна
        self.table_wnd = Toplevel( self.master )
        self.table_wnd.geometry( '1173x448+83+130' )
        self.table_wnd.title( 'Фьючерсы' )
        self.table_wnd.resizable( width=False, height=False )
        self.tableframe = Frame( self.table_wnd, width=870, height=445 )
        self.tableframe.place( x=10, y=10 )
        self.get_filters_values()
        self.filt_torg_date_from = self.mindate
        self.filt_torg_date_to = self.maxdate
        self.filt_fut_from = '-не выбрано-'
        self.filt_quot_from = self.filterquot[0]
        self.filt_quot_to = self.filterquot[1]
    #работа с таблицей
        self.tablemodel = MyTableModel( rows=2000, columns=8 )
        self.table = MyTableCanvas( self.tableframe, self.tablemodel,
                                    cols=8, height=395, width=870,
                                    cellbackgr='white', thefont=( 'TkDefault', 10 ),
                                    rowselectedcolor='blue', read_only=False )
        self.import_table( 'init' )
        self.table.importCSV( 'C:\\temp\\out.csv' )
        self.table.adjustColumnWidths()
        self.table.show()
    #главное меню
        self.main_menu = Menu( self.table_wnd )
        self.table_wnd.config( menu=self.main_menu )
        self.main_menu.add_command( label='Статистические характеристики',
                                    command=self.stat_on )
        self.main_menu.add_command( label='Помощь', command=self.help_on )
    #фрейм "Фильтрация"
        self.filters_label = Label( self.table_wnd, text='Фильтрация', font='TkDefaultFont 12 bold', width=11 )
        self.filters_frame = LabelFrame( self.table_wnd,
                                         width=210,
                                         height=270,
                                         labelwidget=self.filters_label,
                                         labelanchor='n',
                                         text='Фильтрация' )
        self.filters_frame.place( x=955, y=10 )
    #второй фрейм
        self.lower_label = Label( self.table_wnd, text='Таблица', font='TkDefaultFont 12 bold', width=8 )
        self.lower_frame = LabelFrame( self.table_wnd,
                                       width=210,
                                       height=155,
                                       labelwidget=self.lower_label,
                                       labelanchor='n',
                                       text='Таблица' )
        self.lower_frame.place( x=955, y=280 )
    #надпись "Диапазон по дате торгов"
        self.torg_date_label = Label( self.table_wnd, text='Диапазон по дате торгов', font='TkDefaultFont 9 underline', width=24 )
        self.torg_date_label.place( x=973, y=40 )
    #надпись "По имени фьючерса"
        self.name_label = Label( self.table_wnd, text='По имени фьючерса', font='TkDefaultFon, 9 underline', width=24 )
        self.name_label.place( x=973, y=92 )
    #надпись "Диапазон по котировке"
        self.quot_label = Label( self.table_wnd, text='Диапазон по тек. цене', font='TkDefaultFont 9 underline', width=24 )
        self.quot_label.place( x=973, y=144 )
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
        self.torg_date_from.place( x=973, y=62 )
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
        self.torg_date_to.place( x=1061, y=62 )
    #ограничения по выбору дат в календарях, если уже выбрана она из дат
        self.torg_date_from.bind( '<<DateEntrySelected>>', self.from_date_sel )
        self.torg_date_to.bind( '<<DateEntrySelected>>', self.to_date_sel )
    #список с выбором имени фьючерса
        self.name_menu = Combobox( self.table_wnd, state="readonly", font='TkDefaultFont 10 bold' )
        self.name_menu['values'] = tuple( self.fut_names )
        self.name_menu.current(0)
        self.name_menu.place( x=973, y=114, width=176 )
    #текстовое поле для ввода левой границы котировки
        self.quot_from = Entry( self.table_wnd, width=12, style='entry_style.TEntry', font='TkDefaultFont 10 bold' )
        self.quot_from.insert( 0, self.filterquot[0] )
        self.quot_from.place( x=973, y=166 )
    #текстовое поле для ввода правой границы котировки
        self.quot_to = Entry( self.table_wnd, width=12, style='entry_style.TEntry', font='TkDefaultFont 10 bold' )
        self.quot_to.insert( 0, self.filterquot[1] )
        self.quot_to.place( x=1061, y=166 )
    #кнопка "Применить фильтры"
        self.append = Button( self.table_wnd, text='Применить фильтры', width=22, command=self.append_on )
        self.append.place( x=988, y=210 )
    #кнопка "Сбросить фильтры"
        self.clear = Button( self.table_wnd, text='Сбросить фильтры', width=22, command=self.clear_on )
        self.clear.place( x=988, y=240 )
    #кнопка "Сохранить изменения"
        self.save = Button( self.table_wnd, text='Сохранить изменения', width=22, command=self.save_on )
        self.save.place( x=988, y=310 )
    #кнопка "Откатить изменения"
        self.undo = Button( self.table_wnd, text='Откатить изменения', width=22, command=self.undo_on )
        self.undo.place( x=988, y=340 )
    #кнопка "Создать отчет"
        self.report = Button( self.table_wnd, text='Создать отчет', width=22, command=self.report_on )
        self.report.place( x=988, y=398 )
    #обработка закрытия окна
        self.table_wnd.protocol( 'WM_DELETE_WINDOW', self.table_wnd_close )

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
            load_table.execute( 'SELECT torg_date, name, day_end, quotation, min_quot, max_quot, num_contr, pokaz FROM f_zb_pok ' +
                                'ORDER BY torg_date ' +
			        'INTO OUTFILE \'C:/temp/out.csv\' ' +
			        'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
			        'LINES TERMINATED BY \'\n\';' )
        elif mode == 'filtering':
            if f_name == '-не выбрано-':
                load_table.execute( 'SELECT torg_date, name, day_end, quotation, min_quot, max_quot, num_contr, pokaz FROM f_zb_pok '
                                    'WHERE torg_date BETWEEN CAST(\'' + l_torg + '\' AS DATE) ' +
                                                        'AND CAST(\'' + r_torg + '\' AS DATE) ' +
                                    'AND quotation BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
                                    'ORDER BY torg_date ' +
                                    'INTO OUTFILE \'C:/temp/out.csv\' ' +
                                    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                                    'LINES TERMINATED BY \'\n\';' )

            else:
                load_table.execute( 'SELECT torg_date, name, day_end, quotation, min_quot, max_quot, num_contr, pokaz FROM f_zb_pok '
                                    'WHERE torg_date BETWEEN CAST(\'' + l_torg + '\' AS DATE) ' +
                                                        'AND CAST(\'' + r_torg + '\' AS DATE) ' +
                                    'AND name=\'' + f_name + '\' ' +
                                    'AND quotation BETWEEN ' + l_quot + ' AND ' + r_quot + ' ' +
                                    'ORDER BY torg_date ' +
                                    'INTO OUTFILE \'C:/temp/out.csv\' ' +
                                    'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                                    'LINES TERMINATED BY \'\n\';' )
        load_table.close()
        get_table.close()
    #переименовать заголовки
        with open( 'C:\\temp\\out.csv', 'r+', newline='' ) as tablefile:
            add_headers = csv.reader( tablefile )
            headers = 'Дата торг.,Код фьюч.,Дата погаш.,Тек.цена,Мин.цена,Макс.цена,Число прод.,Осн.показатель\n'
            for row in add_headers:
                headers += ','.join(row) + '\n'
        with open( 'C:\\temp\\out.csv', 'w+', newline = '' ) as tablefile:
            tablefile.write( headers )

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
                             'FROM f_zb_pok INTO OUTFILE \'C:/temp/maxmin.csv\' '+
                             'FIELDS ENCLOSED BY \'"\' TERMINATED BY \'\n\' LINES TERMINATED BY \'\n\';' )
        load_filter.execute( 'SELECT DISTINCT name FROM f_zb_pok INTO OUTFILE \'C:/temp/fnames.csv\' '+
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
        self.mindate = date.fromisoformat( self.filterdates[0] )
        self.maxdate = date.fromisoformat( self.filterdates[1] )

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
            self.import_table( 'filtering', l_date, r_date, f_name, l_quot, r_quot )
            self.table.adjustColumnWidths()
            self.table.importCSV( 'C:\\temp\\out.csv' )
            self.table.show()
        self.filt_torg_date_from = date.fromisoformat( l_date )
        self.filt_torg_date_to = date.fromisoformat( r_date )
        self.filt_fut_from = f_name
        self.filt_quot_from = l_quot
        self.filt_quot_to = r_quot

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
                    edit_db_cursor.execute( 'DELETE FROM f_zb_pok WHERE (' +
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
                                               defaultextension='.xlsx',
                                               filetypes=[('файл электронных таблиц', '*.xlsx')] )
        if not report == '':
            self.lastsave = os.path.dirname( report )
            wb = Workbook( report )
            sheet = wb.add_worksheet( 'Данные торгов фьючерсами' )
            center_format = wb.add_format( {'align': 'center'} )
            left_format = wb.add_format( {'align':'left'} )
            date_format = wb.add_format( {'num_format': 'dd-mm-yyyy', 'align': 'left'} )
            sheet.merge_range( 'A1:H1', 'Данные торгов фьючерсами', center_format )
            sheet.merge_range( 'A2:F2', 'Диапазон дат', left_format )
            sheet.merge_range( 'A3:G3', 'Выбранный код фьючерса', left_format )
            sheet.merge_range( 'A4:F4', 'Диапазон текущей стоимости', left_format )
            sheet.merge_range( 'A5:H5', ' ', left_format )
            sheet.set_column( 0, 1, 14 )
            sheet.set_column( 2, 2, 16 )
            sheet.set_column( 3, 3, 14 )
            sheet.set_column( 4, 6, 20 )
            sheet.set_column( 7, 7, 22 )
            sheet.write_datetime( 'G2', self.filt_torg_date_from, date_format )
            sheet.write_datetime( 'H2', self.filt_torg_date_to, date_format )
            sheet.write( 'H3', self.filt_fut_from )
            sheet.write( 'G4', self.filt_quot_from )
            sheet.write( 'H4', self.filt_quot_to )
            sheet.write( 'A6', 'Дата торгов' )
            sheet.write( 'B6', 'Код фьючерса' )
            sheet.write( 'C6', 'Дата погашения' )
            sheet.write( 'D6', 'Текущая цена' )
            sheet.write( 'E6', 'Минимальная цена' )
            sheet.write( 'F6', 'Максимальная цена' )
            sheet.write( 'G6', 'Число проданных' )
            sheet.write( 'H6', 'Основной показатель' )
            with open( 'C:\\temp\\out.csv', 'r' ) as to_save:
                rep_table = csv.DictReader( to_save,
                                            fieldnames=( 'Дата торг.', 'Код фьюч.', 'Дата погаш.', 'Тек.цена',
                                                         'Мин.цена', 'Макс.цена', 'Число прод.', 'Осн.показатель' ) )
                row_id = 5
                for row in rep_table:
                    #пропускаем строчку с сокращенными названиями
                    if row_id == 5:
                        pass
                    else:
                        sheet.write_datetime( row_id, 0, date.fromisoformat(row['Дата торг.']), date_format )
                        sheet.write( row_id, 1, row['Код фьюч.'] )
                        sheet.write_datetime( row_id, 2, date.fromisoformat(row['Дата погаш.']), date_format )
                        sheet.write( row_id, 3, row['Тек.цена'] )
                        sheet.write( row_id, 4, row['Мин.цена'] )
                        sheet.write( row_id, 5, row['Макс.цена'] )
                        sheet.write( row_id, 6, row['Число прод.'] )
                        sheet.write( row_id, 7, row['Осн.показатель'] )
                    row_id += 1   
            wb.close()

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

    #создаем окно со статистическими характеристиками
    def stat_on(self):
        self.statwnd = StatWnd( self.master, self.username, self.password, self.mindate, self.maxdate )
            
    #помощь
    def help_on(self):
        os.startfile( os.getcwd().replace('\\','/')+'/help.chm' )

#класс главного окна (невидимого, из которого вызываются остальные окна)
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
