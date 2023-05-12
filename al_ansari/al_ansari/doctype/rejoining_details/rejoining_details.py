# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class RejoiningDetails(Document):

	# update working status on employee master on submission
	def validate(self):
		existing_doc = frappe.db.exists({"doctype":"Rejoining Details","leave_application": self.leave_application})
		if existing_doc and self.is_new() and not self.amended_from:
			frappe.throw("A record is already created against the leave application") 
		self.days_difference = frappe.utils.date_diff(self.actual_rejoining_date,self.initial_rejoin_date)

	def on_submit(self):
		if self.status == "Rejoined":
			#  mark LWP for difference
			if self.days_difference > 0 and self.leave_type == 'Annual Leave':
				leave_doc = frappe.new_doc('Leave Application')
				leave_doc.leave_type = 'Leave Without Pay'
				leave_doc.employee = self.employee
				leave_doc.from_date = self.initial_rejoin_date
				leave_doc.leave_approver = frappe.get_value("Employee",self.employee,['leave_approver'])
				leave_doc.to_date = frappe.utils.add_days(self.initial_rejoin_date,self.days_difference-1)
				leave_doc.follow_via_email = 1
				# leave_doc.rejoining_doc = self.name
				leave_doc.rejoining_details_ref = self.name
				leave_doc.status = 'Approved'
				leave_doc.save()
				leave_doc.submit()

			# mark working status on emp master
			if self.docstatus == 1:
				emp_rec = frappe.get_doc("Employee",{'name':self.employee})
				emp_rec.working_status = "Working"
				emp_rec.save()	
				frappe.msgprint("Employee working status updated in master")

			# update the rejoining entry on respective leave application
			frappe.db.set_value("Leave Application",self.leave_application,"rejoining_details_ref",self.name)

	def on_cancel(self):
		if self.lwp_application:
			lwp_application = frappe.get_doc("Leave Application",self.lwp_application)
			lwp_application.cancel()

		if self.leave_application:
			frappe.db.set_value('Leave Application',self.leave_application,'rejoining_details_ref','')

		emp_rec = frappe.get_doc("Employee",{'name':self.employee})
		emp_rec.working_status = "On Leave"
		emp_rec.save()	
		frappe.msgprint("Employee working status reverted in master")

@frappe.whitelist()
def validate_rejoining_record(leave):
	leave = frappe.get_doc(json.loads(leave))
	rejoing_rec = frappe.db.get_values("Rejoining Details", {"leave_application": leave.name}, "name", as_dict=True)
	if rejoing_rec :
		rejoing_rec = frappe.get_doc("Rejoining Details", rejoing_rec[0]['name'])
	else :
		rejoing_rec = frappe.new_doc("Rejoining Details")
		rejoing_rec.employee = leave.employee
		rejoing_rec.initial_rejoin_date = leave.rejoin_date
		rejoing_rec.leave_type = leave.leave_type
		rejoing_rec.status = "On Leave"
		rejoing_rec.leave_application = leave.name
		rejoing_rec.actual_rejoining_date = frappe.utils.nowdate()
		rejoing_rec.days_difference = frappe.utils.date_diff(frappe.utils.nowdate(),leave.rejoin_date)
	return rejoing_rec.as_dict()