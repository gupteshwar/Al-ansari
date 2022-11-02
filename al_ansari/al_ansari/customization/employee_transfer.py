from __future__ import unicode_literals
import frappe
from frappe.utils import (getdate)
from datetime import datetime
import json
from frappe.utils import date_diff,add_to_date, formatdate, get_link_to_form, getdate, nowdate


def before_submit(doc,method=None):
	for i in doc.transfer_details:
		if i.property == "Payroll Cost Center":
	
			emp_rec = frappe.get_doc("Employee",doc.employee)

			if emp_rec.payroll_cost_center != i.new:
			# make entry in cost center details child table
				if emp_rec.cost_center_details:
					emp_rec.cost_center_details[len(emp_rec.cost_center_details)-1].to_date = frappe.utils.today()
					emp_rec.cost_center_details[len(emp_rec.cost_center_details)-1].no_of_days = date_diff(frappe.utils.today(), emp_rec.cost_center_details[len(emp_rec.cost_center_details)-1].from_date) 
					emp_rec.append('cost_center_details',
						{
							'from_date': add_to_date(datetime.now(), days=1),
							'cost_center': i.new
						})
					emp_rec.save()
				else:
					cost_center_details = []
					emp_rec.append('cost_center_details',
						{
							'from_date': add_to_date(datetime.now(), days=0),
							'cost_center': i.new
						})
					emp_rec.save()