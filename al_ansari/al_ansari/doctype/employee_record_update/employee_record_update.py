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
		if df.fieldtype in [
			"Data","Select","Link","Small Text","Date","Check","Int","Float"
		]:
			if df.fieldname not in [
				"lft","rgt","old_parent","create_user_permission","user_id"
			]:
				fields.append({"value": df.fieldname, "label": df.label})
	return fields