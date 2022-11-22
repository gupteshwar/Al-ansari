# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class EmployeeRecordUpdate(Document):
	def before_submit(self):
		
		# to update record property in Employee Master
		emp_rec = frappe.get_doc('Employee',{'name':self.employee})
		# emp_rec.status = 'Left'

		for i in self.update_details:
			if i.fieldname == 'date_of_joining':
				emp_rec.update({i.fieldname:datetime.strptime(i.new, '%d-%m-%Y')})
			else:	
				emp_rec.update({i.fieldname:i.new})
		emp_rec.save()
		frappe.msgprint("Employee record properties updated successfully")

@frappe.whitelist()
def get_employee_fields_label():
	fields = []
	for df in frappe.get_meta("Employee").get("fields"):
		if df.fieldname in [
			"salutation",
			"user_id",
			"employee_number",
			"employment_type",
			"holiday_list",
			"branch",
			"department",
			"designation",
			"grade",
			"notice_number_of_days",
			"reports_to",
			"leave_policy",
			"company_email",
			"first_name",
			"middle_name",
			"last_name",
			"project",
			"date_of_joining"
		]:
			fields.append({"value": df.fieldname, "label": df.label})
	return fields
