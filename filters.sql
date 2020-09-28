drop procedure filtr;
use fut_cen_bum;
DELIMITER //
CREATE PROCEDURE `filtr` ()
BEGIN
declare begin_torg date;
declare end_torg date;
declare nme varchar(12);
declare begin_quot double;
declare end_quot double;
set begin_torg = '1996-02-05';
set end_torg = '1996-10-30';
set nme = '22020-1503';
set begin_quot = 78.4;
set end_quot = 85;

END//

SELECT * FROM fut_cen_bum.f_zb
WHERE torg_date BETWEEN 'begin_torg' AND 'end_torg'
and name ='nme'
and quotation BETWEEN 'begin_quot' AND 'end_quot';