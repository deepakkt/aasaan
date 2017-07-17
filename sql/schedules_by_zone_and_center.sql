select pg.name, zn.zone_name, cn.center_name, ps.start_date, ps.end_date, ps.event_management_code, ps.online_registration_code
from schedulemaster_programmaster pg,
contacts_zone zn, contacts_center cn,
schedulemaster_programschedule ps
where pg.id = ps.program_id and
ps.center_id = cn.id and
cn.zone_id = zn.id and
start_date >= '2017-04-01'
order by zone_name, center_name, start_date, pg.name

