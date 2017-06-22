delete from statistics_statisticsprogramcounts;

insert into statistics_statisticsprogramcounts(
zone_name, program_name, program_window, program_count,participant_count)
select z.zone_name, p.name, to_char(date_trunc('month', ps.start_date),'yyyy-mm') AS txn_month, count(*) as program_count,  SUM(psc.value) from schedulemaster_programschedule ps,
schedulemaster_programschedulecounts psc, schedulemaster_programmaster p, schedulemaster_programcountmaster pcm, contacts_center c, contacts_zone z
where ps.id=psc.program_id and p.id = ps.program_id and c.zone_id = z.id and ps.center_id = c.id and psc.category_id=pcm.id and pcm.count_category='ORS Participant Count'
group by 1, 2,3;


insert into statistics_statisticsprogramcounts(
zone_name, program_name, program_window, program_count,participant_count) select ps.country, ps.program_name, to_char(date_trunc('month', ps.start_date),'yyyy-mm') AS program_window, count(*) as program_count,
SUM(ps.total_participants) as participant_count from statistics_overseasenrollement ps group by 1, 2,3;


