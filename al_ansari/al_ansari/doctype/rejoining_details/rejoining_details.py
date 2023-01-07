# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RejoiningDetails(Document):
	# pass

	# update working status on employee master on submission
	def validate(self):
		existing_doc = frappe.db.exists({"doctype":"Rejoining Details","leave_application": self.leave_application})
		if existing_doc and self.is_new() and not self.amended_from:
			frappe.throw("A record is already created against the leave application") 
		self.days_difference = frappe.utils.date_diff(self.actual_rejoining_date,self.initial_rejoin_date)
		# if self.days_difference == 0:
		# 	frappe.throw("Record cannot be saved as the Intial Rejoining date is same as the Actual Rejoining date")

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
				leave_doc.follow_via_email = 0
				leave_doc.rejoining_doc = self.name
				leave_doc.save()
				leave_doc.submit()
				# frappe.msgprint("LWP marked. Please check and submit the same")

			# mark working status on emp master
			if self.docstatus == 1:
				emp_rec = frappe.get_doc("Employee",{'name':self.employee})
				emp_rec.working_status = "Working"
				emp_rec.save()	
				frappe.msgprint("Employee working status updated in master")
			# else:
			# 	frappe.throw("Can't update as the rejoin date has to match the current date")

			# update the rejoining entry on respective leave application
			frappe.db.set_value("Leave Application",self.leave_application,"rejoining_details_ref",self.name)