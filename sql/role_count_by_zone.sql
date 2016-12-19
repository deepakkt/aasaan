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
order by 1, 2

