# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class EarnedLeaveDeductions(Document):
	pass

@frappe.whitelist()
def get_applicants(frm):
	print("frm",frm)
	frm = frappe.json.loads(frm)
	print("frm-son",frm.get("from_date"))
	# return frappe.db.sql(""" 
	# 		SELECT employee,employee_name,count(*) as count from `tabAttendance` 
	# 		where status in('Absent')
	# 		and attendance_date between %s and %s
	# 		group by employee
	# 		""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)

	return frappe.db.sql(""" 
				SELECT 
					a.employee,
					la.total_leaves_allocated as el_allocated,
					a.employee_name,
					count(*) as no_of_lwp,
					count(*)/22 as deduction_ratio,
					la.total_leaves_allocated*(count(*)/22) as to_be_deducted,
					la.total_leaves_allocated - (la.total_leaves_allocated*(count(*)/22)) as to_be_allocated
				from `tabAttendance` a, `tabLeave Allocation` la 
				where 
				a.employee = la.employee and
				la.leave_type = 'Annual Leave' and
				a.status in('Absent')
				and a.attendance_date between %s and %s
				group by employee
				""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)