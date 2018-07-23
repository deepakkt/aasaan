with t as (select zone_name as "Zone Name",
           account_type as "Account Type",
		entity_type as "Entity Type",
		budget_code as "Budget Code",
		tracking_no as "Tracking No",
		voucher_date as "Voucher Date",
		program_name as "Program Name",
		center_name as "Center Name",
		program_start_date as "Program Start Date",
		voucher_age as "Voucher Age",
		voucher_type as "Voucher Type",
		expense_head as "Expense Head",
		rco_status as "RCO Voucher Status",
		np_status as "NP Voucher Status",
		expenses_description as "Expenses Description",
		approval_sent_date as "Approval Sent Date",
		approved_date as "Approved Date",
		finance_submission_date as "Finance Submission Date",
		movement_sheet_no as "Movement Sheet No",
		party_name as "Party Name",
		amount as "Amount",
		payment_date as "Payment Date",
		utr_no as "UTR No",
		tds_amount as "TDS Amount"		
           from voucher_snapshot
where created >= current_date - 30
and account_type <> 'Teacher Accounts'
order by zone_name, voucher_date desc, tracking_no)
select json_agg(t) from t;
