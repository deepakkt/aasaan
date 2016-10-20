select * from
(select first_name, last_name, cug_mobile, other_mobile_1, whatsapp_number, primary_email, d.zone_name from 
contacts_contact a, contacts_individualcontactrolecenter b, contacts_center c, contacts_zone d
where a.id = b.contact_id and
c.zone_id = d.id and
b.center_id = c.id
union
select first_name, last_name, cug_mobile, other_mobile_1, whatsapp_number, primary_email, d.zone_name from 
contacts_contact a, contacts_individualcontactrolezone b, contacts_zone d
where a.id = b.contact_id and
b.zone_id = d.id) a
order by zone_name, first_name, last_name
