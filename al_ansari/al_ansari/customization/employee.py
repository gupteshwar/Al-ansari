from __future__ import unicode_literals
import frappe

def before_save(doc,method=None):
	if doc.project:
		project_name = frappe.db.get_value('Project',doc.project,"project_name")
		doc.project_name = project_name
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