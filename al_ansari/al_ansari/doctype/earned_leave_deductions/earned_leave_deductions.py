# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _

class EarnedLeaveDeductions(Document):
	# pass
	def on_submit(self):
		self.negative_leave_allocation()

	def negative_leave_allocation(self):
		allocation_issue = []
		for i in self.deduction_ratio:
			if i.to_be_deducted >0:
				existing_rec= frappe.get_list('Leave Allocation',
					fields= ["name"],
					filters= [
							['from_date',"=",frappe.utils.add_months(self.from_date, 1)],
							['to_date',"=",frappe.utils.add_months(self.to_date, 1)],
							['employee',"=",i.employee_id],
							['leave_type',"=", "Annual Leave"],
							]
					)
				if existing_rec:
					allocation_issue.append(i.employee_id)
				else:
					leave_alloc = frappe.new_doc("Leave Allocation")
					leave_alloc.employee = i.employee_id
					leave_alloc.employee_name = i.employee_name
					leave_alloc.leave_type= "Annual Leave"
					leave_alloc.new_leaves_allocated = -(i.to_be_deducted)
					leave_alloc.from_date = frappe.utils.add_months(self.from_date, 1) # frm.get("from_date")
					leave_alloc.to_date = frappe.utils.add_months(self.to_date, 1) # frm.get("to_date")
					leave_alloc.save()
					leave_alloc.submit()
			else:
				# frappe.throw("No record for making negative entry")
				allocation_issue.append(i.employee_id)

		if len(allocation_issue) >0:
			frappe.throw(_("The entries for the following emplyoees couldn't be done as they may already exist. Please try entering them manually if required and remove from the table to proceed with other records.({0})").format(allocation_issue))
		else:
			frappe.msgprint(_("Allocation records created successfully"))

	@frappe.whitelist()
	def get_applicants(self):
		filters = self.make_filters()
		cond =get_filter_condition(filters)
		employee_list = frappe.db.sql(
		"""
			select
				distinct t1.employee, t1.employee_name
			from
				`tabLeave Application` t1, `tabEmployee` t2
			where
				t1.employee = t2.employee
				and t1.from_date >= '%(from_date)s'
				and t1.to_date <= '%(to_date)s'
				and t2.payroll_cost_center = '%(payroll_cost_center)s'
				%(cond)s 
		"""
			%{
				"from_date": self.from_date,
				"to_date": self.to_date,
				"payroll_cost_center": self.payroll_cost_center,
				'cond':cond
			},
			as_dict=True
		)
		if not employee_list:
			error_msg = _(
				"No employees found for the mentioned criteria:<br>From Date: {0}<br>To Date: {1}<br>Payroll Cost Center: {2}"
			).format(
				frappe.bold(self.from_date),
				frappe.bold(self.to_date),
				frappe.bold(self.payroll_cost_center),
			)
			if self.branch:
				error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
			if self.reporting_manager:
				error_msg += "<br>" + _("Reporting Manager: {0}").format(frappe.bold(self.reporting_manager))
			frappe.throw(error_msg, title=_("No employees found"))

		return employee_list

	def make_filters(self):
		filters = frappe._dict()
		filters["from_date"] = self.from_date
		filters["to_date"] = self.to_date
		filters["reports_to"] = self.reporting_manager
		filters["branch"] = self.branch
		filters["payroll_cost_center"] = self.payroll_cost_center 
		return filters

def get_filter_condition(filters):
	cond = ""
	for f in ["branch", "reports_to"]: 
		if filters.get(f):
			cond += " and t2." + f + " = " + frappe.db.escape(filters.get(f))

	return cond


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
		# print("holiday_count=====>",holiday_count)
		# get leave allocation per month
		# el_allocated = frappe.db.get_value("Leave Allocation",{'employee':item["employee_id"],"leave_type":"Annual Leave"},['monthly_el_allocated']) or 0
		# el_allocated = frappe.db.get_value("Leave Type",{'name':"Annual Leave"},['monthly_allocation']) or 0
		earned_leaves_list = frappe.get_list("Leave Type",fields="name",filters = [["is_earned_leave","=",1]]) 
		el_list =  [d['name'] for d in earned_leaves_list if 'name' in d]

		monthly_el_allocated = frappe.get_list("Leave Allocation",
							fields="monthly_el_allocated", 
							filters = [['employee','=',item["employee_id"]],
									["leave_type",'IN',el_list],
									['leave_policy_assignment','!=',''],
									['docstatus','=',1],
									['from_date',"<=",frm.get("from_date")],
									['to_date',">=",frm.get("from_date")],
									['from_date',"<=",frm.get("to_date")],
									['to_date',">=",frm.get("to_date")]
									],
							order_by = "creation desc"
									) 
		monthly_el_list =  [d['monthly_el_allocated'] for d in monthly_el_allocated if 'monthly_el_allocated' in d]
		el_allocated = sum(monthly_el_list)
		# el_allocated = monthly_el_allocated[0]['monthly_el_allocated'] if monthly_el_allocated else 0
		# get No. of LWP (summation of fraction of LWP on Leave application)
		no_of_lwp = frappe.db.sql(""" 
			SELECT employee,sum(fraction_of_daily_wage) as no_of_lwp 
			from `tabLeave Application` 
			where employee = %s 
			and docstatus = 1
			and from_date >= %s
			and to_date <= %s
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].no_of_lwp or 0
		# print("no_of_lwp=",no_of_lwp)

		no_of_lwp_manual = frappe.db.sql(""" 
			SELECT la.employee,sum(la.total_leave_days) as no_of_lwp
			from `tabLeave Application` la , `tabLeave Type` lt 
			where la.leave_type = lt.name 
			and la.employee = %s 
			and la.docstatus = 1
			and la.from_date >= %s
			and la.to_date <= %s
			and la.fraction_of_daily_wage = 0
			and lt.is_lwp = 1
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].no_of_lwp or 0
		# print("no_of_lwp_manual== ",no_of_lwp_manual)
		if holiday_count:
			working_days.append({"employee":item["employee_id"],"no_of_working_days":(days_of_month-holiday_count),"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual})
		else:
			working_days.append({"employee":item["employee_id"],"no_of_working_days":days_of_month,"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual})

	return working_days