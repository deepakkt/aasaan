select first_name, last_name, cug_mobile, other_mobile_1, whatsapp_number, primary_email, 
zone_name, role_level, string_agg(role_name, ', ') as roles from 
 (
select z.first_name, z.last_name, z.cug_mobile, z.other_mobile_1,
z.whatsapp_number, z.primary_email,
b.role_name, 
case b.role_level when 'CE' then 'Center' when 'ZO' then 'Zone' end as role_level, 
c.zone_name
from contacts_individualcontactrolezone a, contacts_individualrole b, 
contacts_zone c, contacts_contact z
where a.role_id = b.id
and a.zone_id = c.id and
a.contact_id = z.id
union
select z.first_name, z.last_name, z.cug_mobile, z.other_mobile_1,
z.whatsapp_number, z.primary_email,
b.role_name, 
case b.role_level when 'CE' then 'Center' when 'ZO' then 'Zone' end as role_level, 
c.zone_name
from contacts_individualcontactrolecenter a, contacts_individualrole b, 
contacts_zone c, contacts_center d, contacts_contact z
where a.role_id = b.id
and a.center_id = d.id and
d.zone_id = c.id and
a.contact_id = z.id) k
group by 1, 2, 3, 4, 5, 6, 7, 8
order by zone_name, first_name, role_level