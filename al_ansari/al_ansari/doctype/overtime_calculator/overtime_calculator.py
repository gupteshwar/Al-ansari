# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OvertimeCalculator(Document):
	pass

@frappe.whitelist()
def get_employees_on_oc(from_date,to_date):
	# return frappe.db.sql(""" 
	# 	Select 
	# 		sum(ec.actual_hours) as actual_hours,
	# 		max(ec.overtime_rate) as overtime_rate,
	# 		ec.productive_hours,
	# 		sum(ec.productive_hours * ec.overtime_rate) as overtime_amount,
	# 		sum(st.shift_hours) as shift_hours,
	# 		e.name from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e 
	# 		where 
	# 			ec.employee = e.name 
	# 		 	and st.name = e.default_shift
	# 		 	and DATE(ec.time) >= %s
	# 		 	and DATE(ec.time) <= %s
	# 		 	and ec.log_type = 'OUT';
	# 	""",(from_date,to_date),as_dict=1)

	overtime = frappe.db.sql(""" 
		Select 
			ec.name,
			ec.employee,
			max(ec.actual_hours) as actual_hours,
			ec.overtime_rate,
			ec.productive_hours,
			st.shift_hours 
		from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
		where 
			ec.employee = e.name and 
			e.default_shift = st.name and 
			DATE(ec.time) >= %s and 
			DATE(ec.time) <= %s and 
			ec.log_type = 'OUT' 
			group by date(ec.time);
		""",(from_date,to_date),as_dict=1)
	print("overtime = ",overtime)
	result = []
	for item1 in overtime:
		rec = {}
		rec["employee"] = item1["employee"]
		emp = item1["employee"]
		actual_total = 0.00
		productive_total = 0.00
		shift_total = 0.00
		ot_amt = 0.00
		for item2 in overtime:
			if emp == item2["employee"]:
				actual_total += item2["actual_hours"]
				productive_total += (item2["productive_hours"] * abs(item2["shift_hours"]-item2["actual_hours"]))
				shift_total += item2["shift_hours"]
				ot_amt += (item2["overtime_rate"] * item2["productive_hours"])
			else:
				break
	rec["actual_hours"] = actual_total
	rec["productive_hours"] = productive_total
	rec["shift_hours"] = shift_total
	rec["overtime_amount"] = ot_amt
	print("rec = ",rec)
	return rec