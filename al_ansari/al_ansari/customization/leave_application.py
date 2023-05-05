from __future__ import unicode_literals
import frappe
from frappe.utils import (getdate,date_diff,unique)
import datetime
import json
from datetime import timedelta, date, datetime
	
def update_employee_status(doc,method=None):
	if doc.workflow_state == 'On Leave' and (frappe.utils.nowdate()==doc.from_date):
		emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
		emp_rec.working_status = "On Leave"
		emp_rec.save()
		frappe.msgprint("Employee working status updated in master")
	# elif doc.workflow_state == 'Completed' and (frappe.utils.nowdate() == doc.rejoin_date):
	# 	emp_rec = frappe.get_doc("Employee",{'name':doc.employee})
	# 	emp_rec.working_status = "Active"
	# 	emp_rec.save()
	# 	frappe.msgprint("Employee working status updated in master")

	# update the start day & end day on leave application before save
	linked_ppl = frappe.db.get_value("Leave Type",doc.leave_type,"partial_paid_leave")

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

def after_save(doc,method):
	if doc.rejoining_doc != "":
		frappe.db.set_value("Rejoining Details",doc.rejoining_doc,"lwp_application",doc.name)


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

def get_ab_marked_employee_attendance(end_date, employee, start_date,f_holiday_list,no_rec):
		attendances = frappe.get_all(
			"Attendance",
			fields=["name","employee","attendance_date"],
			filters={"employee": employee['employee'],
					"status":"Absent", 
					"docstatus":1,
					"attendance_date": ("between", [start_date, end_date]),
					},
			order_by = "attendance_date"
		)
		lwp_for = "Absent"
		if attendances:
			no_rec = auto_mark_lwp_for_emp(attendances,f_holiday_list,employee,lwp_for,no_rec)
		return no_rec

def get_leave_marked_employee_attendance(end_date, employee, start_date,f_holiday_list,no_rec):
		attendances = frappe.get_all(
			"Attendance",
			fields=["name","employee","attendance_date"],
			filters={"employee": employee['employee'],
					"status":"On Leave", 
					"docstatus":1,
					"attendance_date": ("between", [start_date, end_date]),
					},
			order_by = "attendance_date"
		)
		lwp_for = "On Leave"
		if attendances:
			no_rec = auto_mark_lwp_for_emp(attendances,f_holiday_list,employee,lwp_for,no_rec)
		return no_rec

def get_employee_holiday_list(employee,start_dt,end_dt):
	emp_holiday_list = frappe.get_value('Employee',employee['employee'],'holiday_list')
	if emp_holiday_list:
		holiday_list = frappe.get_all(
			'Holiday',
			fields=["holiday_date"],
			filters={"parent": emp_holiday_list, 
				"holiday_date": ("between", [start_dt, end_dt])}
			,order_by = 'holiday_date'
		)
		f_holiday_list = [d["holiday_date"] for d in holiday_list if "holiday_date" in d]
		return f_holiday_list
	else:
		frappe.throw("Holiday List is not assigned on Employee Master")

def auto_mark_lwp_for_emp(attendances,f_holiday_list,employee,lwp_for,no_rec):
	if len(attendances)>0:
		f_attendance_list = [ad["attendance_date"] for ad in attendances if "attendance_date" in ad]
		ab_attendance_list = [ad["name"] for ad in attendances if "name" in ad]
		
		if lwp_for == 'Absent':

			if len(f_attendance_list)>0:
				mark_lwp = calculate_dates_for_auto_lwp(f_holiday_list,f_attendance_list)
			if mark_lwp:
				# cancel absent attendance
				for ab_attendance in ab_attendance_list:
					ab_doc = frappe.get_doc('Attendance',ab_attendance)
					ab_doc.cancel()

				for ml in mark_lwp:
					leave_app = frappe.new_doc('Leave Application')
					leave_app.employee = employee['employee']
					leave_app.leave_type = 'Leave Without Pay'
					leave_app.leave_approver = frappe.get_value('Employee',employee['employee'],'leave_approver')
					leave_app.from_date = ml[0]
					leave_app.to_date = ml[len(ml)-1]
					leave_app.status = "Approved"
					leave_app.save()
					leave_app.submit()
			else:
				no_rec.append(employee['employee'])

		elif lwp_for == 'On Leave':
			if len(f_attendance_list)>0:
				mark_lwp = calculate_dates_for_auto_lwp(f_holiday_list,f_attendance_list)
			if mark_lwp:
				for ml in mark_lwp:
					lwp_dates = [item for item in ml if item not in f_attendance_list]#ml- f_attendance_list
					# check if lwp dates are consecutive 
					if len(lwp_dates)>0:
						consecutive_lwp_dates = check_lwp_dates_are_consecutive(lwp_dates)
						if len(consecutive_lwp_dates)==1:#len(lwp_dates) > 0:
							leave_app = frappe.new_doc('Leave Application')
							leave_app.employee = employee['employee']
							leave_app.leave_type = 'Leave Without Pay'
							leave_app.leave_approver = frappe.get_value('Employee',employee['employee'],'leave_approver')
							leave_app.from_date = lwp_dates[0]
							leave_app.to_date = lwp_dates[len(lwp_dates)-1]
							leave_app.status = "Approved"
							leave_app.save()
							leave_app.submit()
						else:
							for cld in consecutive_lwp_dates:
								leave_app = frappe.new_doc('Leave Application')
								leave_app.employee = employee['employee']
								leave_app.leave_type = 'Leave Without Pay'
								leave_app.leave_approver = frappe.get_value('Employee',employee['employee'],'leave_approver')
								leave_app.from_date = cld[0]
								leave_app.to_date = cld[len(cld)-1]
								leave_app.status = "Approved"
								leave_app.save()
								leave_app.submit()

			else:
				no_rec.append(employee['employee'])
			
	return no_rec

def check_lwp_dates_are_consecutive(lwp_dates):
	con_lwp_list = [] 
	con_lwp = []
	for idx in range(len(lwp_dates)):
		c=1
		con_lwp.append(lwp_dates[idx])
		if(lwp_dates[idx] + timedelta(days=c) in lwp_dates):
			con_lwp.append(lwp_dates[idx] + timedelta(days=c))
		else:
			con_lwp_list.append(con_lwp)
			con_lwp = []
	return con_lwp_list

@frappe.whitelist()
def validate_to_mark_lwp(payroll_entry):
	payroll_entry = json.loads(payroll_entry)
	employees = payroll_entry['employees']
	start_dt = datetime.strptime(payroll_entry['start_date'], '%Y-%M-%d' )
	end_dt = datetime.strptime(payroll_entry['end_date'], '%Y-%M-%d' )
	no_rec = []
	for rec in range(len(employees)):
		f_holiday_list = get_employee_holiday_list(employees[rec],payroll_entry['start_date'],payroll_entry['end_date'])
		no_rec = get_leave_marked_employee_attendance(payroll_entry['end_date'],employees[rec],payroll_entry['start_date'],f_holiday_list,no_rec)
		no_rec = get_ab_marked_employee_attendance(payroll_entry['end_date'],employees[rec],payroll_entry['start_date'],f_holiday_list,no_rec)
		
	return no_rec

def calculate_dates_for_auto_lwp(f_holiday_list,f_attendance_list):
	ab = []
	consecutive_ab = []
	c = 0
	for idx in range(len(f_attendance_list)):
		c=1
		if not consecutive_ab:
			consecutive_ab.append(f_attendance_list[idx])	
		if(f_attendance_list[idx] + timedelta(days=c) in f_attendance_list):
			consecutive_ab.append(f_attendance_list[idx] + timedelta(days=c))
			c+=1
		elif(f_attendance_list[idx] + timedelta(days=c) not in f_attendance_list):
			ab.append(consecutive_ab)
			consecutive_ab = []

	wo =[]
	consecutive_wo = []
	for idx in range(len(f_holiday_list)):
		c=1
		if not consecutive_wo:
			consecutive_wo.append(f_holiday_list[idx])	
		if(f_holiday_list[idx] + timedelta(days=c) in f_holiday_list):
			consecutive_wo.append(f_holiday_list[idx] + timedelta(days=c))
			c+=1
		elif(f_holiday_list[idx] + timedelta(days=c) not in f_holiday_list):
			wo.append(consecutive_wo)
			consecutive_wo = []

	sandwich = []
	paycut = []
	for w in wo:
		previous_day = w[0]-timedelta(days=1)
		next_day = w[len(w)-1]+timedelta(days=1)
		if(previous_day in f_attendance_list and next_day in f_attendance_list):
			sandwich.append(w)
		elif(previous_day in f_attendance_list and w[0]+timedelta(days=1) in f_holiday_list):
			paycut.append(w)
		elif(w[len(w)-1]+timedelta(days=1) not in f_holiday_list and w[len(w)-1]+timedelta(days=1) in f_attendance_list):
			paycut.append(w)

	all_lwp = ab + sandwich + paycut
	flat_lwp = [element for innerList in all_lwp for element in innerList]
	flat_lwp = sorted(flat_lwp)
	
	mark_lwp = []
	consecutive_lwp = []
	for idx in range(len(flat_lwp)):
		c=1
		if not consecutive_lwp:
			consecutive_lwp.append(flat_lwp[idx])	
		if(flat_lwp[idx] + timedelta(days=c) in flat_lwp):
			consecutive_lwp.append(flat_lwp[idx] + timedelta(days=c))
			c+=1
		elif(flat_lwp[idx] + timedelta(days=c) not in flat_lwp):
			mark_lwp.append(consecutive_lwp)
			consecutive_lwp = []

	return mark_lwp