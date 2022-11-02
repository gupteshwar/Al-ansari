from __future__ import unicode_literals
import frappe
from frappe.utils import (getdate)
import datetime
	
def update_employee_status(doc,method=None):
	if doc.workflow_state == 'On Leave' and (frappe.utils.nowdate()>=doc.from_date):
		emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
		emp_rec.working_status = "On Leave"
		emp_rec.save()
		frappe.msgprint("Employee status update in master")
	elif doc.workflow_state == 'Completed' and (frappe.utils.nowdate() == doc.rejoin_date):
		emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
		emp_rec.working_status = "Active"
		emp_rec.save()
		frappe.msgprint("Employee status update in master")

def check_update_working_status_for_leave():
	leave_app_list = frappe.db.get_list('Leave Application',{'from_date':frappe.utils.nowdate()})
	cur_date = datetime.datetime.now()
	if leave_app_list:
		for leave_app in leave_app_list:
			l_app = frappe.get_doc('Leave Application',leave_app.name)
			if l_app.workflow_state == 'On Leave' and (datetime.datetime.now().date()>=l_app.from_date):
				emp_rec = frappe.get_doc('Employee',l_app.employee)
				emp_rec.working_status = 'On Leave'

# overriding core whitelisted method for employee transfer
@frappe.whitelist()
def get_employee_fields_label():
	fields = []
	for df in frappe.get_meta("Employee").get("fields"):
		if df.fieldname in [
			"salutation",
			"payroll_cost_center",		# customized-additional field added to list
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