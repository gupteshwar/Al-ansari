# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeRecordUpdate(Document):
	pass

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
		]:
			fields.append({"value": df.fieldname, "label": df.label})
	return fields
