# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _

class EarnedLeaveDeductions(Document):
	# pass
	def validate(self):
		if self.deduction_ratio:
			for d in reversed(range(len(self.deduction_ratio))):
				if self.deduction_ratio[d].to_be_deducted == 0:
					self.remove(self.deduction_ratio[d])
				else:
					existing_rec = frappe.get_list('Leave Allocation',
					fields= ["name"],
					filters= [
							['edl_from_date',"=",frappe.utils.add_months(self.from_date, 1)],
							['edl_to_date',"=",frappe.utils.add_months(self.to_date, 1)],
							['employee',"=",self.deduction_ratio[d].employee_id],
							['leave_type',"=", "Annual Leave"],
							['docstatus','=',1]
						]
					)
					if existing_rec:
						self.remove(self.deduction_ratio[d])


	def on_submit(self):
		allocation_na = []
		if self.deduction_ratio:
			for d in range(len(self.deduction_ratio)):
				if not self.deduction_ratio[d].allocation_from_date or not self.deduction_ratio[d].allocation_end_date:
					allocation_na.append(self.deduction_ratio[d].employee_id)
		else:
			frappe.throw(_("There are no entries to be calculated for the selected filters"))

		if allocation_na:
			frappe.throw(_("Allocation not available for the records {0}").format(allocation_na))
		self.negative_leave_allocation()

	def on_cancel(self):
		self.cancel_negative_leave_allocation_eld()

	def negative_leave_allocation(self):
		allocation_issue = []
		duplication_issue = []
		for i in self.deduction_ratio:
			if i.to_be_deducted >0:
				existing_rec= frappe.get_list('Leave Allocation',
					fields= ["name"],
					filters= [
							['edl_from_date',"=",frappe.utils.add_months(self.from_date, 1)],
							['edl_to_date',"=",frappe.utils.add_months(self.to_date, 1)],
							['employee',"=",i.employee_id],
							['leave_type',"=", "Annual Leave"],
							['docstatus','=',1]
						]
					)
				if existing_rec:
					duplication_issue.append(i.employee_id)
				else:
					if i.allocation_from_date and i.allocation_end_date:
						leave_alloc = frappe.new_doc("Leave Allocation")
						leave_alloc.employee = i.employee_id
						leave_alloc.employee_name = i.employee_name
						leave_alloc.leave_type= "Annual Leave"
						leave_alloc.new_leaves_allocated = -(i.to_be_deducted)
						leave_alloc.edl_from_date = frappe.utils.add_months(self.from_date, 1) # frm.get("from_date")
						leave_alloc.edl_to_date =  frappe.utils.add_months(self.to_date, 1) # frm.get("to_date")
						leave_alloc.from_date = i.allocation_from_date 		# frappe.utils.add_months(self.from_date, 1) # frm.get("from_date")
						leave_alloc.to_date = i.allocation_end_date 	# frappe.utils.add_months(self.to_date, 1) # frm.get("to_date")
						leave_alloc.save()
						leave_alloc.submit()
					else:
						allocation_issue.append(i.employee_id)
			else:
				# frappe.throw("No record for making negative entry")
				allocation_issue.append(i.employee_id)

		if len(duplication_issue) >0:
			frappe.throw(_("The entries for the following employees couldn't be done as they may already exist. Please try entering them manually if required and remove from the table to proceed with other records.({0})").format(duplication_issue))
		elif len(allocation_issue) > 0:
			frappe.throw(_("Please check the EL allocation is proper and updated in the Earned Leave Deduction record else remove the record to proceed with other records.({0})").format(allocation_issue))
		else:
			frappe.msgprint(_("Allocation records created successfully"))

	def cancel_negative_leave_allocation_eld(self):
		emp_rec = self.deduction_ratio
		to_cancel = []
		leave_all_eld = frappe.get_list('Leave Allocation',
					fields= ["name","employee","new_leaves_allocated"],
					filters= [
							['edl_from_date',"=",frappe.utils.add_months(self.from_date, 1)],
							['edl_to_date',"=",frappe.utils.add_months(self.to_date, 1)],
							['leave_type',"=", "Annual Leave"],
							['docstatus',"=",1]
						])
		
		issue_to_cancel = []
		emp_flatlist = [emp.get('employee_id') for emp in emp_rec if emp.get('employee_id')]

		for eld in leave_all_eld:
			if eld["employee"] in emp_flatlist:
				try:
					leave_alloc_doc = frappe.get_doc("Leave Allocation",eld["name"])
					leave_alloc_doc.cancel()
				except:
					issue_to_cancel.append(eld["employee"])
		if len(issue_to_cancel)>0:
			frappe.throw(_("Unable to cancel the following records {0}")).format(issue_to_cancel)

	@frappe.whitelist()
	def get_applicants(self):
		filters = self.make_filters()
		cond =get_filter_condition(filters)
		employee_list = frappe.db.sql(
		"""
			select
				distinct t1.employee, t1.employee_name
			from
				`tabAttendance` t1, `tabEmployee` t2
			where
				t1.employee = t2.employee
				and t2.status = 'Active'
				and t1.attendance_date between '%(from_date)s' and '%(to_date)s'
				%(cond)s 
		"""
			%{
				"from_date": self.from_date,
				"to_date": self.to_date,
				'cond':cond
			},
			as_dict=True
		)
		if not employee_list:
			error_msg = _(
				"No employees found for the mentioned criteria:<br>From Date: {0}<br>To Date: {1}"
			).format(
				frappe.bold(self.from_date),
				frappe.bold(self.to_date),
			)
			if self.branch:
				error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
			if self.reporting_manager:
				error_msg += "<br>" + _("Reporting Manager: {0}").format(frappe.bold(self.reporting_manager))
			if self.payroll_cost_center:
				error_msg += "<br>" + _("Payroll Cost Center: {0}").format(frappe.bold(self.payroll_cost_center))
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
	for f in ["branch", "reports_to","payroll_cost_center"]: 
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
							fields=["monthly_el_allocated","from_date","to_date"], 
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
		if monthly_el_allocated:
			monthly_el_list =  [d['monthly_el_allocated'] for d in monthly_el_allocated if 'monthly_el_allocated' in d]
			el_allocated = sum(monthly_el_list)
		no_of_lwp = frappe.db.sql(""" 
			Select 
				sum(t2.fraction) as no_of_lwp
			from `tabLeave Application` t1,`tabELD Fraction Monthly` t2 
			where 
				t1.name = t2.parent and
				t2.from_date>= %s and 
				t2.to_date<=%s and t1.employee = %s
				and t1.docstatus = 1""",(frm.get("from_date"),frm.get("to_date"),item["employee_id"]),as_dict=1)[0].no_of_lwp or 0

		no_of_lwp_manual = frappe.db.sql(""" 
			SELECT employee,count(name) as no_of_lwp
			from `tabAttendance`
			where leave_type = "Leave Without Pay"
			and employee = %s 
			and docstatus = 1
			and attendance_date between %s AND %s
			""",(item["employee_id"],frm.get("from_date"),frm.get("to_date")),as_dict=1)[0].no_of_lwp or 0

		if monthly_el_allocated:
			if holiday_count:
				working_days.append({"employee":item["employee_id"],"no_of_working_days":(days_of_month-holiday_count),"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual,"days_of_month":days_of_month,"allocation_from_date":monthly_el_allocated[0].from_date if monthly_el_allocated[0].from_date else None,"allocation_end_date":monthly_el_allocated[0].to_date if monthly_el_allocated[0].to_date else None})
			else:
				working_days.append({"employee":item["employee_id"],"no_of_working_days":days_of_month,"el_allocated":el_allocated,"no_of_lwp":no_of_lwp+no_of_lwp_manual,"days_of_month":days_of_month,"allocation_from_date":monthly_el_allocated[0].from_date if monthly_el_allocated[0].from_date else None,"allocation_end_date":monthly_el_allocated[0].to_date if monthly_el_allocated[0].to_date else None})
		else:
			if holiday_count:
				working_days.append({"employee":item["employee_id"],"no_of_working_days":(days_of_month-holiday_count),"el_allocated":0,"no_of_lwp":no_of_lwp+no_of_lwp_manual,"days_of_month":days_of_month,"allocation_from_date":None,"allocation_end_date":None})
			else:
				working_days.append({"employee":item["employee_id"],"no_of_working_days":days_of_month,"el_allocated":0,"no_of_lwp":no_of_lwp+no_of_lwp_manual,"days_of_month":days_of_month,"allocation_from_date":None,"allocation_end_date":None})

	return working_days