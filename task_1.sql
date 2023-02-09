with op as (
	select accountid,
		   count(id) as totalWons,
		   CAST((current_date - max(closingdate)) / 30.417 as int) as monthSinceWon
	from opportunities
		where stage = 'Won'
	group by accountid
	order by accountid
),
rev as (
	select op.accountid,
		   sum(r.revenue) as totalRev
	from revenue r
	left join opportunities op on op.id = r.opportunityid
	group by 1
	order by 1
),
main as (
	select ac.companyname,
		   case 
				when op.monthSinceWon > 24 then 1
				when op.monthSinceWon > 18 and op.monthSinceWon <= 24 then 2
				when op.monthSinceWon > 12 and op.monthSinceWon <= 18 then 3
				when op.monthSinceWon > 6 and op.monthSinceWon <= 12 then 4
				when op.monthSinceWon <= 6 and op.monthSinceWon >= 0 then 5 
					else 0
		   end as recency,
		   case 
				when op.totalWons >= 1 and op.totalWons <= 3 then 1
				when op.totalWons >= 4 and op.totalWons <= 10 then 2
				when op.totalWons >= 11 and op.totalWons <= 30 then 3
				when op.totalWons >= 31 and op.totalWons <= 60 then 4
				when op.totalWons > 60 then 5
					else 0
		   end as frequency,
		   case	
				when rev.totalRev <= 100000 and rev.totalRev > 0 then 1
				when rev.totalRev > 100000 and rev.totalRev <= 300000 then 2 
				when rev.totalRev > 300000 and rev.totalRev <= 1000000 then 3
				when rev.totalRev > 1000000 and rev.totalRev <= 3000000 then 4
				when rev.totalRev > 3000000 then 5 
					else 0
		   end as monetary
	from op
	left join rev on rev.accountid = op.accountid
	left join accounts ac on ac.id = op.accountid
)

select companyname,
	   recency,
	   frequency,
	   monetary,
	   segmentlabel
from main
left join segment_codes sc on sc.recencyscore = main.recency
								and sc.frequencyscore = main.frequency
								and sc.monetaryscore = main.monetary
