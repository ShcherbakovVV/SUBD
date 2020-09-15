use fut_cen_bum;

create table if not exists f_zb_notvalid( 
name text not null,
quotation double not null,
min_quot double not null,
max_quot double not null,
num_contr int not null
); #таблица для некорректных записей таблицы f_zb 
insert into f_zb_notvalid select f_zb.name, f_zb.quotation, f_zb.min_quot, f_zb.max_quot, f_zb.num_contr from f_zb 
where length(f_zb.name)>12 or f_zb.quotation<0 or f_zb.min_quot<0 or f_zb.max_quot<0 or f_zb.num_contr<0;

create table if not exists zb_notvalid( 
name text not null,
base text not null
); #таблица для некорректных записей таблицы zb 
insert into zb_notvalid select zb.name, zb.base from zb 
where length(zb.name)>12 or length(zb.base)>11;
