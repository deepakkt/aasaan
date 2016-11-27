delete from reports_ircdashboardmissingroles;

/* insert query into target table */
insert into reports_ircdashboardmissingroles
(zone_name, center_name, role_level, available_roles, missing_roles)
/* select the values from the inner tables */
select x1.zone_name, x1.center_name, 'Center', coalesce(available_roles, ''), coalesce(missing_roles, '') from
/* This segment selects the missing roles. It does a 
cartesian product of center and center roles
and then matches with the available roles in the center role 
definitions in contacts_IndividualContactRoleCenter*/
(select zone_name, center_name, string_agg(role_name, ', ') as missing_roles
 from
(select z.zone_name, c.center_name, b.role_name
from 
contacts_center c,
contacts_individualrole b,
contacts_zone z
where b.role_level = 'CE'
and c.zone_id = z.id
and (c.id, b.id) not in
(select distinct center_id, role_id from 
contacts_IndividualContactRoleCenter)
order by 1, 2, 3) a
group by 1, 2) x1
/* left outer join because we want
centers without roles also to come up*/
LEFT OUTER JOIN  
/* available roles is much simpler. a simple join
is sufficient. However we must do distinct because 
multiple contacts may be dinfed for the same center and role*/
(select zone_name, center_name, string_agg(role_name, ', ') as available_roles from
(select distinct z.zone_name, c.center_name, r.role_name from 
contacts_IndividualContactRoleCenter cr,
contacts_center c,
contacts_zone z,
contacts_individualrole r
where c.id = cr.center_id and
c.zone_id = z.id and
cr.role_id = r.id
order by 1, 2, 3) a
group by 1, 2) x2
ON x1.center_name = x2.center_name and x1.zone_name = x2.zone_name;


delete from reports_ircdashboardzonesummary;

/* slightly complex sql
remember that each count is taken through a count(*) sql
grouped by zone
each segment is then left outer joined through the other table
finally the entire chunk is left outer joined with the zone 
master. it is necessary to do this because joins will skip
zones with no data. we want them with zero values if absent
*/
insert into reports_ircdashboardzonesummary
(zone_name, center_count, teacher_count, program_count)
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
order  by 1;

delete from reports_ircdashboardprogramcounts;

insert into reports_ircdashboardprogramcounts
(zone_name, program_name, program_count, program_window)
select z.zone_name, p.name, count(*) as program_count, 'past' from
schedulemaster_programmaster p, schedulemaster_programschedule ps,
contacts_center c, contacts_zone z
where
ps.program_id = p.id
and
end_date <= current_date and
end_date >= (current_date - 45)
and
ps.center_id = c.id and
c.zone_id = z.id
group by 1, 2 order by 1, 2;

insert into reports_ircdashboardprogramcounts
(zone_name, program_name, program_count, program_window)
select z.zone_name, p.name, count(*) as program_count, 'future' from
schedulemaster_programmaster p, schedulemaster_programschedule ps,
contacts_center c, contacts_zone z
where
ps.program_id = p.id
and
start_date >= current_date and
start_date <= (current_date + 45)
and
ps.center_id = c.id and
c.zone_id = z.id
group by 1, 2 order by 1, 2;


delete from reports_ircdashboardrolesummary;

insert into reports_ircdashboardrolesummary
(zone_name, role_name, role_count)
select zone_name, role_name, role_count from
(select z.zone_name, r.role_name, count(*) as role_count from
contacts_IndividualContactRoleCenter cr, contacts_zone z,
contacts_individualrole r, contacts_center c
where
cr.center_id = c.id and
c.zone_id = z.id and
cr.role_id = r.id
group by 1, 2
union all
select z.zone_name, r.role_name, count(*) from
contacts_IndividualContactRoleZone cr, contacts_zone z,
contacts_individualrole r
where
cr.zone_id = z.id and
cr.role_id = r.id
group by 1, 2) x
order by 1, 2;

delete from reports_ircdashboardsectorcoordinators;


insert into reports_ircdashboardsectorcoordinators
(zone_name, full_name, centers)
select zone_name, first_name || ' ' || last_name as name, string_agg(center_name, ', ') from
(select z.zone_name, c.first_name, c.last_name, ce.center_name
from contacts_contact c, contacts_center ce,
contacts_IndividualContactRoleCenter b,
contacts_zone z, 
contacts_individualrole r
where b.center_id = ce.id and
c.id = b.contact_id and
ce.zone_id = z.id and
b.role_id = r.id and
role_name = 'Sector Coordinator'
order by 1, 2, 3, 4) a
group by 1, 2
order by 1, 2;

delete from reports_ircdashboardcentermap;

insert into reports_ircdashboardcentermap
(zone_name, center_name, latitude, longitude, recent_program_count)
select zone_name, center_name, latitude, longitude, sum(coalesce(x2.program_count, 0)) as program_count from
(select zone_name, center_name, c.id, latitude, longitude
from 
contacts_zone z, contacts_center c
where z.id = c.zone_id) x1
LEFT OUTER JOIN
(select center_id, 1 as program_count from
schedulemaster_programschedule where end_date >= (current_date - 90)) x2
on x1.id = x2.center_id
group by 1, 2, 3, 4
order by 1, 2, 3, 4;