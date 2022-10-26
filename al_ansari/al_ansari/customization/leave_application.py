from __future__ import unicode_literals
import frappe

def update_employee_status(doc,method=None):
	frappe.msgprint(doc.employee)
	if doc.workflow_state == 'On Leave':
		emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
		emp_rec.working_status = "On Leave"
		emp_rec.save()
		frappe.msgprint("Employee status update in master")
	elif doc.workflow_state == 'Completed':
		emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
		emp_rec.working_status = "Active"
		emp_rec.save()
		frappe.msgprint("Employee status update in master")