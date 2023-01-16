# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class PartialPayrollBankEntry(Document):
	def on_submit(self):
		# custom_code block start 12Jan2023
		# update value on Payroll Entry to process particular emp sal
		frappe.db.set_value("Payroll Entry",self.payroll_entry,"partial_entry",self.name)
		payroll_doc = frappe.get_doc("Payroll Entry",self.payroll_entry)
		
		existing_rec = frappe.db.sql("""Select t2.employee from `tabPartial Payroll Bank Entry` t1, `tabPartial Payroll Employee Detail` t2
		where t1.name = t2.parent and t1.payroll_entry = %s and t1.name = %s """,(self.payroll_entry,self.name),as_list=1)
		if existing_rec:
			existing_rec_list = [element for innerList in existing_rec for element in innerList]


		for x in payroll_doc.employees:
			if(x.employee in existing_rec_list):
				x.update({"status": "In Process"})

		payroll_doc.save()
		frappe.msgprint("Please navigate to the Payroll to make payment by clicking the payroll_entry field")
		# custom_code block end 12Jan2023

@frappe.whitelist()
def make_partial_entry(rec,selections):
	# make entry in Partial Payroll Bank Entry
	rec = json.loads(rec)
	selections = json.loads(selections)
	if rec:
		if(len(rec)) == 1:
			rec.append("00test")
			record = tuple(rec)
		elif len(rec)>1:
			record = tuple(rec)

	emp_list = frappe.db.sql("""Select employee,employee_name from `tabPayroll Employee Detail` 
		where name IN {0}""".format(record),as_dict=1)

	existing_rec = frappe.db.sql("""Select t2.employee from `tabPartial Payroll Bank Entry` t1, `tabPartial Payroll Employee Detail` t2
	where t1.name = t2.parent and t1.payroll_entry = %s and t1.docstatus!=2""",(selections[0]),as_list=1)
	existing_rec_list = []
	if existing_rec:
		existing_rec_list = [element for innerList in existing_rec for element in innerList]
	emp_exists = []
	if existing_rec_list and emp_list:
		for emp in emp_list:
			if emp['employee'] in existing_rec_list:
				emp_exists.append(emp['employee'])
	
	if emp_exists:
		return {"exists":1,"value":emp_exists}
	else:
		doc =frappe.get_doc({
		    'doctype': 'Partial Payroll Bank Entry',
		    'payroll_entry':selections[0]
		})
		for emp in emp_list:
			doc.append("employees",emp)
		doc.save()
		return {"exists":0,"value":doc.name}

