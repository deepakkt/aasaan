/* select the values from the inner tables */
select x1.zone_name, x1.center_name, available_roles, missing_roles from
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
ON x1.center_name = x2.center_name and x1.zone_name = x2.zone_name


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
ON x1.center_name = x2.center_name and x1.zone_name = x2.zone_name

