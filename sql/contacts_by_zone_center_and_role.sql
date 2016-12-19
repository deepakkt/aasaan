select c.zone_name, d.center_name, b.role_name, z.first_name, z.last_name, z.cug_mobile, z.other_mobile_1,
z.whatsapp_number, z.primary_email
from contacts_individualcontactrolecenter a, contacts_individualrole b, 
contacts_zone c, contacts_center d, contacts_contact z
where a.role_id = b.id
and a.center_id = d.id and
d.zone_id = c.id and
a.contact_id = z.id
order by zone_name, center_name, role_name, first_name