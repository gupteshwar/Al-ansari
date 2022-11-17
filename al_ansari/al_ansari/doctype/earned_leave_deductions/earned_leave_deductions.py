# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class EarnedLeaveDeductions(Document):
	pass


@frappe.whitelist()
def no_of_working_days_employeewise(frm):
	frm = frappe.json.loads(frm)

	days_of_month = frappe.db.sql("""SELECT DAYOFMONTH(LAST_DAY(%s)) as days_of_month""",(frm.get("from_date")),as_dict=1)[0].days_of_month

	deduction_ratio = frm.get("deduction_ratio")
	working_days = []
	for item in deduction_ratio:
		holiday_count = frappe.db.sql(""" 
				Select count(*) as h_count from `tabHoliday` h,`tabHoliday List` hl, `tabEmployee` e 
				where h.parent=hl.name  
				and e.holiday_list = hl.name 
				and e.name = %s 
				and h.holiday_date between %s and %s;
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].h_count
		print("holiday_count=====>",holiday_count)
		# get leave allocation per month
		el_allocated = frappe.db.get_value("Leave Allocation",{'employee':item["employee_id"],"leave_type":"Annual Leave"},['monthly_el_allocated']) or 0
		
		# get No. of LWP (summation of fraction of LWP on Leave application)
		no_of_lwp = frappe.db.sql(""" 
			SELECT employee,sum(fraction_of_daily_wage) as no_of_lwp 
			from `tabLeave Application` 
			where employee = %s 
			and docstatus = 1
			and from_date >= %s
			and to_date <= %s
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].no_of_lwp or 0
		print("no_of_lwp=",no_of_lwp)
		no_of_lwp_manual = frappe.db.sql(""" 
			SELECT employee,sum(total_leave_days) as no_of_lwp
			from `tabLeave Application` 
			where employee = %s 
			and docstatus = 1
			and from_date >= %s
			and to_date <= %s
			and fraction_of_daily_wage = 0
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].no_of_lwp or 0
		print("no_of_lwp_manual== ",no_of_lwp_manual)
		if holiday_count:
			working_days.append({"employee":item["employee_id"],"no_of_working_days":(days_of_month-holiday_count),"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual})
		else:
			working_days.append({"employee":item["employee_id"],"no_of_working_days":days_of_month,"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual})

	return working_days

@frappe.whitelist()
def get_applicants(frm):
	frm = frappe.json.loads(frm)
	# calulate to total absent days
	# return frappe.db.sql(""" 
	# 		SELECT employee,employee_name,count(*) as count from `tabAttendance` 	
	# 		where status in('Absent')
	# 		and attendance_date between %s and %s
	# 		group by employee
	# 		""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)

	# return frappe.db.sql(""" 
	# 			SELECT 
	# 				a.employee,
	# 				la.monthly_el_allocated as el_allocated,
	# 				a.employee_name,
	# 				count(*) as no_of_lwp,
	# 				count(*)/22 as deduction_ratio,
	# 				la.monthly_el_allocated*(count(*)/22) as to_be_deducted,
	# 				la.monthly_el_allocated - (la.monthly_el_allocated*(count(*)/22)) as to_be_allocated
	# 			from `tabAttendance` a, `tabLeave Allocation` la 
	# 			where 
	# 			a.employee = la.employee and
	# 			la.leave_type = 'Annual Leave' and
	# 			a.status in('Absent')
	# 			and a.attendance_date between %s and %s
	# 			group by employee
	# 			""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)


	# calculate total LWP from leave application
	# return frappe.db.sql(""" 
	# 			SELECT 
	# 				a.employee,
	# 				a.employee_name,
	# 				count(*) as no_of_lwp
	# 			from `tabAttendance` a, `tabLeave Allocation` la 
	# 			where 
	# 			a.employee = la.employee and
	# 			la.leave_type = 'Annual Leave' and
	# 			a.status in('Absent','On Leave')
	# 			and a.attendance_date between %s and %s
	# 			group by employee
	# 			""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)

	return frappe.db.sql(""" 
				SELECT 
					DISTINCT(employee),
					employee_name
				from `tabLeave Application`
				where 
				from_date >= %s
				and to_date <= %s""",(frm.get("from_date"),frm.get("to_date")),as_dict=1)

@frappe.whitelist()
def negative_ledger_entry(frm):
	frm = frappe.json.loads(frm)
	deduction_ratio = frm.get("deduction_ratio")
	for i in deduction_ratio:
		if i["to_be_deducted"] != 0:
			leave_alloc = frappe.new_doc("Leave Allocation")
			leave_alloc.employee = i["employee_id"]
			leave_alloc.employee_name = i["employee_name"]
			leave_alloc.leave_type= "Annual Leave"
			leave_alloc.new_leaves_allocated = -(i["to_be_deducted"])
			leave_alloc.from_date = frappe.utils.add_months(frm.get("from_date"), 1) # frm.get("from_date")
			leave_alloc.to_date = frappe.utils.add_months(frm.get("end_date"), 1) # frm.get("to_date")
			print("leave_alloc==>",leave_alloc.new_leaves_allocated)
			leave_alloc.save()
			# leave_alloc.submit()
		else:
			frappe.throw("No record for making negative entry")
