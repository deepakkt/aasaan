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
order by 1, 2

