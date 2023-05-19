# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json

class OvertimeCalculator(Document):
	# pass
	def validate(self):
		if len(self.overtime_calculator_detail)>0:
			for ocd in range(len(self.overtime_calculator_detail)):
				self.overtime_calculator_detail[ocd].actual_hours = round(self.overtime_calculator_detail[ocd].holiday_actual_hours,2) +round(self.overtime_calculator_detail[ocd].non_holiday_actual_hours,2)
				self.overtime_calculator_detail[ocd].holiday_productive_hours = (round(self.overtime_calculator_detail[ocd].holiday_overtime,2) * round(self.overtime_calculator_detail[ocd].productive_hours_ratio,2))
				self.overtime_calculator_detail[ocd].non_holiday_productive_hours = round(self.overtime_calculator_detail[ocd].non_holiday_overtime,2)* round(self.overtime_calculator_detail[ocd].productive_hours_ratio,2)
				self.overtime_calculator_detail[ocd].holiday_overtime_amount = round(self.overtime_calculator_detail[ocd].holiday_productive_hours,2) * self.overtime_calculator_detail[ocd].holiday_overtime_rate
				self.overtime_calculator_detail[ocd].non_holiday_overtime_amount = round(self.overtime_calculator_detail[ocd].non_holiday_productive_hours,2) * self.overtime_calculator_detail[ocd].non_holiday_overtime_rate
				self.overtime_calculator_detail[ocd].overtime_amount = self.overtime_calculator_detail[ocd].holiday_overtime_amount + self.overtime_calculator_detail[ocd].non_holiday_overtime_amount

	def on_submit(self):
		if not self.overtime_calculator_detail:
			frappe.throw("The Overtime Calculator Details table cannot be empty.")
		additional_salary_entry(self)	

@frappe.whitelist()
def autofill_employees(payroll_entry):
	payroll_entry = frappe.get_doc(json.loads(payroll_entry))
	oc_doc = frappe.new_doc("Overtime Calculator")
	oc_doc.from_date = payroll_entry.start_date
	oc_doc.to_date = payroll_entry.end_date
	oc_doc.payroll_date = payroll_entry.posting_date
	oc_doc.branch = payroll_entry.branch
	oc_doc.payroll_cost_center = payroll_entry.cost_center
	# for emp in payroll_entry.employees:
	# 	oc_doc.append('overtime_calculator_detail',{"employee":emp.employee,"employee_name":emp.employee_name})
	emp_list = []
	for emp in payroll_entry.employees:
		employee_name,hourly_rate,grade = frappe.get_value('Employee',emp.employee,["employee_name","hourly_rate","grade"])
		emp_list.append({"name":emp.employee,"employee_name":employee_name ,"hourly_rate": hourly_rate,"productive_hours_ratio":frappe.get_value("Employee Grade",grade,["productive_hours_ratio"])})
		
	print("EMPLIST==",emp_list)
	if emp_list:
		valid_emp_list = validate_employees_on_oc(payroll_entry.start_date,payroll_entry.end_date,emp_list)
	if valid_emp_list:
		for emp in valid_emp_list:
			oc_doc.append('overtime_calculator_detail',
				{"employee":emp["name"],
				"employee_name":emp["employee_name"],
				"productive_hours_ratio":emp["productive_hours_ratio"],
				"hourly_rate":emp["hourly_rate"],
				"holiday_overtime_rate":emp["holiday_overtime_rate"],
				"holiday_overtime":emp["holiday_overtime"],
				"holiday_actual_hours":emp["holiday_actual_hours"],
				"h_shift_total":emp["h_shift_total"],
				"non_holiday_overtime_rate":emp["non_holiday_overtime_rate"],
				"non_holiday_overtime":emp["non_holiday_overtime"],
				"non_holiday_actual_hours":emp["non_holiday_actual_hours"],
				"nh_shift_total":emp["nh_shift_total"],
				"shift_hours":emp["shift_hours"]
				})
	return oc_doc.as_dict()	


def validate_employees_on_oc(from_date,to_date,emp_list):
	if emp_list:
		for emp in emp_list:
			h_overtime = frappe.db.sql(""" 
				Select 
					ec.name,
					ec.employee,
					ec.employee_name,
					max(ec.actual_hours) as actual_hours,
					ec.overtime_rate,
					ec.productive_hours,
					st.shift_hours ,
					ec.time,
					ec.is_holiday
				from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
				where 
					ec.employee = e.name and 
					e.default_shift = st.name and 
					DATE(ec.time) >= %s and 
					DATE(ec.time) <= %s and 
					ec.log_type = 'OUT' and
					e.working_status != 'On Leave' and
					e.name = %s and
					ec.is_holiday = 1
					group by date(ec.time)
					order by date(ec.time) desc;
				""",(from_date,to_date,emp["name"]),as_dict=1)

			nh_overtime = frappe.db.sql(""" 
				Select 
					ec.name,
					ec.employee,
					ec.employee_name,
					max(ec.actual_hours) as actual_hours,
					ec.overtime_rate,
					ec.productive_hours,
					st.shift_hours ,
					ec.time,
					ec.is_holiday
				from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
				where 
					ec.employee = e.name and 
					e.default_shift = st.name and 
					DATE(ec.time) >= %s and 
					DATE(ec.time) <= %s and 
					ec.log_type = 'OUT' and
					e.working_status != 'On Leave' and
					e.name = %s and
					ec.is_holiday = 0
					group by date(ec.time)
					order by date(ec.time) desc;
				""",(from_date,to_date,emp["name"]),as_dict=1)

			final_shift_total = 0.00
			h_actual_total = 0.00
			holiday_overtime_total = 0.00
			h_shift_total = 0.00
			nh_actual_total = 0.00
			non_holiday_overtime_total = 0.00
			nh_shift_total = 0.00
			if h_overtime :
				emp.update({
					"employee_name":h_overtime[0]["employee_name"] ,
					# "productive_hours_ratio":frappe.get_value("Employee Grade",emp["grade"],["productive_hours_ratio"])#h_overtime[0]["productive_hours"] 
					})
			if nh_overtime:
				emp.update({
					"employee_name":nh_overtime[0]["employee_name"],
					# "productive_hours_ratio":frappe.get_value("Employee Grade",emp["grade"],["productive_hours_ratio"])#nh_overtime[0]["productive_hours"]
					})

			if h_overtime:
				ot_amt = 0.00

				for h_ot in h_overtime:
					h_actual_total += h_ot["actual_hours"]
			# 		print("ot_hr ==",round((item2["actual_hours"]-item2["shift_hours"]),2) * item2["productive_hours"]*item2["overtime_rate"])
					holiday_overtime_total += h_ot["actual_hours"] # -h_ot["shift_hours"] if (h_ot["actual_hours"]>h_ot["shift_hours"]) else 0
					# h_shift_total += h_ot["shift_hours"]
					# ot_amt += item2["overtime_rate"] * (item2["productive_hours"] * round((item2["actual_hours"]-item2["shift_hours"]),2))
				
				emp.update({
					"holiday_overtime_rate":h_overtime[0]["overtime_rate"],
					"holiday_overtime":holiday_overtime_total,
					"holiday_actual_hours":h_actual_total,
					"h_shift_total":h_shift_total
					})
			else:
				emp.update({
					"holiday_overtime_rate":0 ,#frappe.get_value("Employee",emp["name"],["h_ot_rate"]),
					"holiday_overtime":holiday_overtime_total,
					"holiday_actual_hours":h_actual_total,
					"h_shift_total":h_shift_total
					})

			if nh_overtime:	
				ot_amt = 0.00

				for nh_ot in nh_overtime:
					nh_actual_total += nh_ot["actual_hours"]
			# 		print("ot_hr ==",round((item2["actual_hours"]-item2["shift_hours"]),2) * item2["productive_hours"]*item2["overtime_rate"])
					non_holiday_overtime_total += nh_ot["actual_hours"]-nh_ot["shift_hours"] if (nh_ot["actual_hours"]>nh_ot["shift_hours"]) else 0
					nh_shift_total += nh_ot["shift_hours"]
					# ot_amt += item2["overtime_rate"] * (item2["productive_hours"] * round((item2["actual_hours"]-item2["shift_hours"]),2))
				
				emp.update({
					"non_holiday_overtime_rate":nh_overtime[0]["overtime_rate"],
					"non_holiday_overtime":non_holiday_overtime_total,
					"non_holiday_actual_hours":nh_actual_total,
					"nh_shift_total":nh_shift_total
					})

			else:
				emp.update({
					"non_holiday_overtime_rate": 0 ,#frappe.get_value("Employee",emp["name"],["nh_ot_rate"]),
					"non_holiday_overtime":non_holiday_overtime_total,
					"non_holiday_actual_hours":nh_actual_total,
					"nh_shift_total":nh_shift_total
					})

			emp.update({
				"shift_hours":round(emp["h_shift_total"] + emp["nh_shift_total"],2),
				"hourly_rate":emp["hourly_rate"]
				})

	return emp_list

@frappe.whitelist()
def get_employees_on_oc(from_date,to_date,branch,reporting_manager,payroll_cost_center):
	emp_list = []

	if reporting_manager == " " and branch !=" ":
		emp_list = frappe.db.get_list('Employee',
		    filters={
		        'branch': branch,
		        'status': 'Active',
		        'payroll_cost_center':payroll_cost_center

		    },
		    fields=['name','employee_name','hourly_rate','grade']
		)

	if branch == " " and reporting_manager !=" ":
		emp_list = frappe.db.get_list('Employee',
		    filters={
		        'reports_to': reporting_manager,
		        'status': 'Active',
		        'payroll_cost_center':payroll_cost_center
		    },
		    fields=['name','employee_name','hourly_rate','grade']
		)

	if branch != " " and reporting_manager != " ":
		emp_list = frappe.db.get_list('Employee',
		    filters={
		    	'branch': branch,
		        'reports_to': reporting_manager,
		        'status': 'Active',
		        'payroll_cost_center':payroll_cost_center
		    },
		    fields=['name','employee_name','hourly_rate','grade']
		)

	if branch == " " and reporting_manager ==" ":
		frappe.throw("Please select either branch or reporting manager")

	if emp_list:
		for emp in emp_list:
			productive_hours_ratio = frappe.get_value("Employee Grade",emp["grade"],"productive_hours_ratio")
			h_overtime = frappe.db.sql(""" 
				Select 
					ec.name,
					ec.employee,
					ec.employee_name,
					max(ec.actual_hours) as actual_hours,
					ec.overtime_rate,
					ec.productive_hours,
					st.shift_hours ,
					ec.time,
					ec.is_holiday
				from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
				where 
					ec.employee = e.name and 
					e.default_shift = st.name and 
					DATE(ec.time) >= %s and 
					DATE(ec.time) <= %s and 
					ec.log_type = 'OUT' and
					e.working_status != 'On Leave' and
					e.name = %s and
					ec.is_holiday = 1
					group by date(ec.time)
					order by date(ec.time) desc;
				""",(from_date,to_date,emp["name"]),as_dict=1)

			nh_overtime = frappe.db.sql(""" 
				Select 
					ec.name,
					ec.employee,
					ec.employee_name,
					max(ec.actual_hours) as actual_hours,
					ec.overtime_rate,
					ec.productive_hours,
					st.shift_hours ,
					ec.time,
					ec.is_holiday
				from `tabEmployee Checkin` ec, `tabShift Type` st,`tabEmployee` e  
				where 
					ec.employee = e.name and 
					e.default_shift = st.name and 
					DATE(ec.time) >= %s and 
					DATE(ec.time) <= %s and 
					ec.log_type = 'OUT' and
					e.working_status != 'On Leave' and
					e.name = %s and
					ec.is_holiday = 0
					group by date(ec.time)
					order by date(ec.time) desc;
				""",(from_date,to_date,emp["name"]),as_dict=1)
			emp.update({
				"productive_hours_ratio":productive_hours_ratio
				})
			final_shift_total = 0.00
			h_actual_total = 0.00
			holiday_overtime_total = 0.00
			h_shift_total = 0.00
			nh_actual_total = 0.00
			non_holiday_overtime_total = 0.00
			nh_shift_total = 0.00
			if h_overtime :
				emp.update({
					"employee_name":h_overtime[0]["employee_name"] ,
					})
			if nh_overtime:
				emp.update({
					"employee_name":nh_overtime[0]["employee_name"],
					})

			if h_overtime:
				ot_amt = 0.00

				for h_ot in h_overtime:
					h_actual_total += h_ot["actual_hours"]
					holiday_overtime_total += h_ot["actual_hours"] 
				
				emp.update({
					"holiday_overtime_rate":h_overtime[0]["overtime_rate"],
					"holiday_overtime":holiday_overtime_total,
					"holiday_actual_hours":h_actual_total,
					"h_shift_total":h_shift_total
					})
			else:
				emp.update({
					"holiday_overtime_rate":0 ,
					"holiday_overtime":holiday_overtime_total,
					"holiday_actual_hours":h_actual_total,
					"h_shift_total":h_shift_total
					})

			if nh_overtime:	
				ot_amt = 0.00

				for nh_ot in nh_overtime:
					nh_actual_total += nh_ot["actual_hours"]
					non_holiday_overtime_total += nh_ot["actual_hours"]-nh_ot["shift_hours"] if (nh_ot["actual_hours"]>nh_ot["shift_hours"]) else 0
					nh_shift_total += nh_ot["shift_hours"]
				
				emp.update({
					"non_holiday_overtime_rate":nh_overtime[0]["overtime_rate"],
					"non_holiday_overtime":non_holiday_overtime_total,
					"non_holiday_actual_hours":nh_actual_total,
					"nh_shift_total":nh_shift_total
					})

			else:
				emp.update({
					"non_holiday_overtime_rate":0 ,
					"non_holiday_overtime":non_holiday_overtime_total,
					"non_holiday_actual_hours":nh_actual_total,
					"nh_shift_total":nh_shift_total
					})

			emp.update({
				"shift_hours":round(emp["h_shift_total"] + emp["nh_shift_total"],2),
				"hourly_rate":emp["hourly_rate"]
				})

	return emp_list

def additional_salary_entry(self):
	pending_list = []
	created_list = []
	for rec in range(len(self.overtime_calculator_detail)):
		if(frappe.db.get_value("Additional Salary",{"employee":self.overtime_calculator_detail[rec].employee,"salary_component":"Overtime","payroll_date":self.payroll_date})):
			pending_list.append(self.overtime_calculator_detail[rec].idx)
			frappe.throw(_("Additional Salary component is already created for row {0}. Please remove the entry from child table and then try to submit.").format(self.overtime_calculator_detail[rec].idx))
		else:
			if self.overtime_calculator_detail[rec].overtime_amount > 0:
				add_sal_doc = frappe.new_doc("Additional Salary")
				add_sal_doc.employee = self.overtime_calculator_detail[rec].employee
				add_sal_doc.salary_component = "Overtime"
				add_sal_doc.amount = self.overtime_calculator_detail[rec].overtime_amount
				add_sal_doc.payroll_date = self.payroll_date
				add_sal_doc.save()
				add_sal_doc.submit()
				created_list.append(self.overtime_calculator_detail[rec].idx)
			else:
				pending_list.append(self.overtime_calculator_detail[rec].employee)
				frappe.throw(_("Additional Salary Entry not done for the following records: {0}").format(pending_list))