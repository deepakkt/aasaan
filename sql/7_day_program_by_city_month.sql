select p.name, c.city, cast(extract(year from start_date) as char(4)) || '-' || cast(extract(month from start_date) as char(2)) as month
from schedulemaster_programschedule a,
contacts_center c, schedulemaster_programmaster p
where start_date >= current_date
and a.center_id = c.id and
a.program_id = p.id and
(name like 'Inner Engineering%' or name like 'Isha Yoga%')