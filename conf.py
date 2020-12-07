import os, math, time, mysql.connector

if os.path.exists('C:\\temp\\pok.csv'):
    os.remove('C:\\temp\\pok.csv')
get_pok = mysql.connector.connect( host = 'localhost',
                                   database = 'fut_cen_bum',
                                   user = self.username,
                                   password = self.password )
get_pok._open_connection()
load_pok = get_pok.cursor()
load_pok.execute( 'SELECT (@row_number:=@row_number + 1) AS id, torg_date, f_zb.name, exec_date, day_end, quotation, min_quot, max_quot, num_contr FROM f_zb, zb ' +
                  'WHERE f_zb.name=zb.name ' +
                  'ORDER BY f_zb.name, torg_date ' +
                  'INTO OUTFILE \'C:/temp/pok.csv\' ' +
                  'FIELDS ENCLOSED BY \'"\' TERMINATED BY \',\' ' +
                  'LINES TERMINATED BY \'\n\';' )
load_pok.close()
get_pok.close()
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
                tablefile.write( pr_sps[i] + str(pokazat) + '"\n' )

