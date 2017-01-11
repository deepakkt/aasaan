-- Complex query. Let's break it down

-- root declarative select after everything is built
select mcm.zone_name, mcm.center_name, mcm.name as item_name,

-- make any non entered values zero
coalesce(m.quantity, 0) as quantity from

(
-- build a cartesian product of all zones, centers and materials
select zone_name, center_name, name from 

(select name from materials_itemmaster
where name in 
('Amplifier', 
'Battery', 
'Chair', 
'Column Speaker', 
'DVD Player', 
'Gurupooja Set', 
'Invertor', 
'Green Carpet', 
'Orange Carpet', 
'Projector', 
'Projector Screen', 
'Sadhguru Class Photo', 
'Sadhguru Intiation Photo')
order by 1) im, 

contacts_center, contacts_zone
-- join above cartesian product to give proper zone and center names
where contacts_center.zone_id = contacts_zone.id) mcm

LEFT OUTER JOIN

-- get actually entered values from materials table
(select z.zone_name, c.center_name, item.name, cm.quantity
from
materials_centermaterial cm,
contacts_zone z,
contacts_center c,
materials_itemmaster item
where cm.center_id = c.id and
c.zone_id = z.id
and cm.item_id = item.id) m
ON mcm.zone_name = m.zone_name and mcm.center_name = m.center_name and
mcm.name = m.name
order by 1, 2, 3