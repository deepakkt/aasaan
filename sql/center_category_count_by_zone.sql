select center_category, count(*) as center_count
from 
contacts_center c, contacts_zone z
where c.zone_id = z.id
and z.zone_name = 'TN North'
group by 1
order by 1