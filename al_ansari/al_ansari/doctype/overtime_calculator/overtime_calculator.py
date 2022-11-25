# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

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
			ec.employee_name,
			max(ec.actual_hours) as actual_hours,
			ec.overtime_rate,
			ec.productive_hours,
			st.shift_hours ,
			ec.time
		from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
		where 
			ec.employee = e.name and 
			e.default_shift = st.name and 
			DATE(ec.time) >= %s and 
			DATE(ec.time) <= %s and 
			ec.log_type = 'OUT' 
			group by date(ec.time);
		""",(from_date,to_date),as_dict=1)
	# print("overtime = ",overtime)
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
				ot_amt += (item2["overtime_rate"] * round((item2["productive_hours"] * abs(item2["shift_hours"]-item2["actual_hours"])),2))
				# print("Overtime======",abs(item2["shift_hours"]-item2["actual_hours"]))
		rec["employee_name"] = item1["employee_name"]
		rec["actual_hours"] = actual_total
		rec["productive_hours"] = productive_total
		rec["shift_hours"] = shift_total
		rec["overtime_amount"] = ot_amt
		
		result.append(rec)
	# print("result = ",result)

	final_res = {record['employee']:record for record in result}.values()
	
	return final_res

@frappe.whitelist()
def additional_salary_entry(frm):
	frm = frappe.json.loads(frm)
	pending_list = []
	created_list = []
	for rec in frm["overtime_calculator_detail"]:
		if(frappe.db.get_value("Additional Salary",{"employee":rec["employee"],"salary_component":"Overtime","payroll_date":frappe.utils.nowdate()})):
			pending_list.append(rec["idx"])
			frappe.throw(	_("Additional Salary component is already created for row {0}").format(rec["idx"]))
		else:
			add_sal_doc = frappe.new_doc("Additional Salary")
			add_sal_doc.employee = rec["employee"]
			add_sal_doc.salary_component = "Overtime"
			add_sal_doc.amount = rec["overtime_amount"]
			add_sal_doc.payroll_date = frappe.utils.nowdate()
			add_sal_doc.save()
			created_list.append(rec["idx"])
			frappe.msgprint("Additional Salary component created successfully")