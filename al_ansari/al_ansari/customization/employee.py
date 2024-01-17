from __future__ import unicode_literals
import frappe

def before_save(doc,method=None):
	if doc.project:
		project_name = frappe.db.get_value('Project',doc.project,"project_name")
		doc.project_name = project_name
	doc.h_ot_rate = doc.hourly_rate * doc.h_ot_multiplier
	doc.nh_ot_rate = doc.hourly_rate * doc.nh_ot_multiplier
	# # updating the cost center in child table alon wih dates and cost center
	# # frappe.throw(doc.is_new())
	# if doc.is_new() == 0:
	# 	emp_rec = frappe.get_doc("Employee",doc.name)
	# 	if emp_rec.payroll_cost_center != doc.payroll_cost_center:
	# 		# make entry in cost center details child table
	# 		if emp_rec.cost_center_details:
	# 			emp_rec[len(emp_rec.cost_center_details)].to_date = frappe.utils.today()
	# 			emp_rec[len(emp_rec.cost_center_details)].no_of_days = date_diff(frappe.utils.today(), emp_rec[len(emp_rec.cost_center_details)].from_date) 
	# 			emp_rec = emp_rec.cost_center_details.append(
	# 				{
	# 					'from_date': add_to_date(datetime.now(), days=1),
	# 					'cost_center': doc.payroll_cost_center
	# 				})
	# 		else:
	# 			emp_rec.cost_center_details = []
	# 			emp_rec = emp_rec.cost_center_details.append(
	# 				{
	# 					'from_date': add_to_date(datetime.now(), days=0),
	# 					'cost_center': doc.payroll_cost_center
	# 				})
	# 	emp_rec.save()

def valid_employee_adv(doc,method):
	start_dt = frappe.db.sql("""SELECT DATE(CONCAT(YEAR(CURDATE()),'-01-01')) st_dt""",as_dict=1)[0].st_dt
	end_dt = frappe.db.sql("""SELECT DATE(CONCAT(YEAR(CURDATE()),'-12-31')) ed_dt""",as_dict=1)[0].ed_dt
	total_adv = frappe.db.sql(""" 
			Select sum(return_amount) as return_total,
			 		sum(advance_amount) as advance_total,
					sum(claimed_amount) as claimed_total
			from `tabEmployee Advance`
			where
				employee = %s and
				docstatus = 1 and
				posting_date between %s and %s
		""",(doc.employee,start_dt,end_dt),as_dict=1)

	advance_limit = frappe.get_value('Employee',doc.employee,'advance_limit')
	if len(total_adv)>=1:
		if (advance_limit-(total_adv[0].advance_total-total_adv[0].claimed_total-total_adv[0].return_total)) <= 0:
			frappe.throw("The advance amount cannot be zero or less than zero")
		else:
			if((advance_limit-(total_adv[0].advance_total-total_adv[0].claimed_total-total_adv[0].return_total)) < doc.advance_amount):
				frappe.throw("The advance amount cannot exceed the advance limit amount")