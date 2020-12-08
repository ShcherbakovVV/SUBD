import os, csv, math, time, mysql.connector

#загрузка пароля и логина
with open( 'logpswd.txt', 'r+', newline='' ) as logpswd:
    read_lp = csv.reader( logpswd )
    log_pass = []
    for row in read_lp:
        row = str(row)
        log_pass.append( str(row)[2:len(row)-3] )
    username = log_pass[0]
    password = log_pass[1]

#функция для расчета rk
def rk( F, Tu, Tn ):
    d1 = time.strptime( Tu, "%Y-%m-%d" )
    d2 = time.strptime( Tn, "%Y-%m-%d" )
    if F == 0:
        return 1
    else:
        return (math.log(F/100))/(d2.tm_yday - d1.tm_yday)

#создание упорядоченной промежуточной таблицы
if os.path.exists('C:\\temp\\pok.csv'):
    os.remove('C:\\temp\\pok.csv')
get_pok = mysql.connector.connect( host = 'localhost',
                                   database = 'fut_cen_bum',
                                   user = username,
                                   password = password )
get_pok._open_connection()
curs_get_pok = get_pok.cursor()
curs_get_pok.execute( 'SELECT torg_date, f_zb.name, exec_date, day_end, quotation, min_quot, max_quot, num_contr FROM f_zb, zb ' +
                      'WHERE f_zb.name=zb.name ' +
                      'ORDER BY f_zb.name, torg_date ' +
                      'INTO OUTFILE \'C:/temp/pok.csv\' ' +
                      'FIELDS ENCLOSED BY \'"\' ' +
                      'TERMINATED BY "," ' +
                      'LINES TERMINATED BY "\n";' )
curs_get_pok.close()
get_pok.close()

#расчет показателя
pr_sps = []
with open( 'C:\\temp\\pok.csv', 'r+', newline='' ) as tablefile1:
    read_pok = csv.reader( tablefile1 )
    for row in read_pok:
        row = str(row)
        pr_sps += [ row[1:len(row)-1] ]
    name_zap = '00000-0000'
    i = 0
    with open( 'C:\\temp\\pok2.csv', 'w+', newline='' ) as tablefile2:
        while i < len( pr_sps ):
            dan_tek = pr_sps[i].split('\'')
            if name_zap != dan_tek[3]:
                num = 1
                name_zap = dan_tek[3]
                tablefile2.write( pr_sps[i] + ', \'0\'\n')
                i += 1
            elif num == 1:
                tablefile2.write( pr_sps[i] + ', \'0\'\n')
                i += 1
                num = 2
            else:
                dan_tek_2 = pr_sps[i-2].split('\'')
                pokazat = math.log( abs(rk( float(dan_tek[9]), dan_tek[5], dan_tek[7] )/rk( float(dan_tek_2[9]), dan_tek_2[5], dan_tek_2[7] )))
                tablefile2.write( pr_sps[i] + ', \'' + str(pokazat) + '\'\n' )
                i += 1
                
#агрузка таблицы с показателями в БД
load_pok = mysql.connector.connect( host = 'localhost',
                                    database = 'fut_cen_bum',
                                    user = username,
                                    password = password )
load_pok._open_connection()
curs_load_pok = load_pok.cursor()
curs_load_pok.execute( 'DROP TABLE IF EXISTS f_zb_pok; ')
curs_load_pok.execute( 'CREATE TABLE f_zb_pok ( ' +
                           'torg_date DATE NOT NULL, ' +
                           'name VARCHAR(12) NOT NULL, ' +
                           'exec_date DATE NOT NULL, ' +
                           'day_end DATE NOT NULL, ' +
                           'quotation DOUBLE NOT NULL, ' +
                           'min_quot DOUBLE NOT NULL, ' +
                           'max_quot DOUBLE NOT NULL, ' +
                           'num_contr INT NOT NULL, ' +
                           'pokaz DOUBLE NOT NULL );' ) 
curs_load_pok.execute( 'LOAD DATA INFILE \'C:/temp/pok2.csv\' ' +
                       'INTO TABLE f_zb_pok ' + 
                       'FIELDS ENCLOSED BY "\'" ' +
                       'TERMINATED BY ", " ' +
                       'LINES TERMINATED BY "\n";' )
curs_load_pok.close()
load_pok.close()              


