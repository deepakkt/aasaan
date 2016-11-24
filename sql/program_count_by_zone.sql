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
group by 1, 2 order by 1, 2


