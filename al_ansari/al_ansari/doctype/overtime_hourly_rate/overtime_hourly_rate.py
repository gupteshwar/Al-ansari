# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OvertimeHourlyRate(Document):
	pass


@frappe.whitelist()
def get_hourly_rate_details(grade):
	emp_list = frappe.db.sql("""
		SELECT e.name,e.employee_name,s.base 
		FROM `tabEmployee` e,`tabSalary Structure Assignment` s 
		WHERE 
			e.name= s.employee 
			and e.grade = %s
		""",(grade),as_dict=1)
	return emp_list