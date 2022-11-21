from __future__ import unicode_literals
import frappe
from frappe.utils import (getdate,date_diff)
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

	# update the start day & end day on leave application before save
	linked_ppl = frappe.db.get_value("Leave Type",doc.leave_type,"partial_paid_leave")
	print("linked_ppl==>",linked_ppl)
	if linked_ppl:
		approved_leave_count = frappe.db.sql(""" 
				SELECT
					la.name,
					la.status,
					la.from_date,
					la.to_date,
					la.total_leave_days,
					sum(la.total_leave_days) as count,
					la.leave_type 
				FROM `tabLeave Application` la,`tabLeave Type` lt 
				WHERE 
					la.leave_type = lt.name
					and lt.is_pplbd = 1 
					and la.status ='Approved' 
					and lt.is_ppl= 0 
					and lt.is_lwp = 0
					and la.docstatus = 1
					and la.from_date>= %s
					and la.to_date<= %s
					and la.employee = %s
			""",(frappe.defaults.get_user_default("year_start_date"),
				frappe.defaults.get_user_default("year_end_date"),
				doc.employee),as_dict=1)
		print("approved_leave_count==",approved_leave_count) 

		if approved_leave_count[0].name != None:

			doc.start_day = approved_leave_count[0].count+1 
			doc.end_day = doc.start_day + date_diff(doc.to_date,doc.from_date)+1

			fraction_master = frappe.get_doc("Partial Paid Leave",linked_ppl)
			ct = doc.start_day
			c=0 
			frac_of_day = 0
			while ct < doc.end_day:
				print("ct==",ct)
				for item in fraction_master.partial_paid_leave_item:
					if item.start_day <= ct <= item.end_day:
						frac_of_day += item.fraction_of_daily_salary_per_leave
				ct +=1
				c+=1
				# print("frac_of_day==",frac_of_day)
			doc.fraction_of_daily_wage = c - frac_of_day
			# print("IF",doc.fraction_of_daily_wage)
		else:
			doc.start_day = 0
			doc.end_day = date_diff(doc.to_date,doc.from_date) +1
			fraction_master = frappe.get_doc("Partial Paid Leave",linked_ppl)
			ct = doc.start_day
			c=0 
			frac_of_day = 0
			while ct<=doc.end_day:
				for item in fraction_master.partial_paid_leave_item:
					if item.start_day <= ct <= item.end_day:
						frac_of_day += item.fraction_of_daily_salary_per_leave
				ct +=1
				c+=1
			doc.fraction_of_daily_wage = c - frac_of_day
			# print("start_day",doc.start_day)
			# print("end_day",doc.end_day)

# to be excuted through scheduler crons
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