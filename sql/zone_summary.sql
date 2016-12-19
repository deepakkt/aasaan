/* slightly complex sql
remember that each count is taken through a count(*) sql
grouped by zone
each segment is then left outer joined through the other table
finally the entire chunk is left outer joined with the zone 
master. it is necessary to do this because joins will skip
zones with no data. we want them with zero values if absent
*/
select x1.zone_name, coalesce(x2.center_count, 0) as center_count, 
coalesce(x2.teacher_count, 0) as teacher_count, 
coalesce(x2.program_count, 0) as program_count 
from 
contacts_zone x1
LEFT OUTER JOIN
(select x1.zone_name, coalesce(x1.center_count, 0) as center_count, 
coalesce(x1.teacher_count, 0) as teacher_count, 
coalesce(x2.program_count, 0) as program_count 
from
(select x1.zone_name, x1.center_count, x2.teacher_count from
(select zone_name, count(*) as center_count from
contacts_center c, contacts_zone z
where c.zone_id = z.id
group by 1 order by 1) x1
LEFT OUTER JOIN
(select zone_name, count(*) as teacher_count from contacts_individualcontactrolezone cr,
contacts_individualrole r,
contacts_zone z
where cr.role_id = r.id
and r.role_name = 'Teacher'
and cr.zone_id = z.id
group by 1 order by 1) x2
ON x1.zone_name = x2.zone_name) x1
LEFT OUTER JOIN
(select zone_name, count(*) as program_count from 
schedulemaster_programschedule ps, contacts_center c, contacts_zone z
where ps.center_id = c.id and
c.zone_id = z.id
and start_date >= current_date
group by 1 order by 1) x2
ON x1.zone_name = x2.zone_name) x2
ON x1.zone_name = x2.zone_name
order  by 1