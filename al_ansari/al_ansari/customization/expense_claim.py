from __future__ import unicode_literals
import frappe


def transfer_child_attachment_to_parent(doc,method=None):
	attachments = []
	if doc.docstatus != 0:
		if len(doc.expenses)>0:
			for expense in doc.expenses:
				attachments.append(expense.attachment)
				print("attachment",expense.attachment)
	if attachments:
		for attachment in attachments:
			print("url==",attachment)
			file_rec = frappe.get_doc('File',{"file_url":attachment})
			file_rec.attached_to_name = doc.name
			file_rec.save()

def check_validation(doc,method=None):
	for expense in doc.expenses:

		exp_rec = frappe.db.sql(""" 
			Select name from `tabExpense Claim Detail`
			where expense_date = %s
			and supplier = %s
			and supplier_invoice_number = %s
			and docstatus = 1
		""",(expense.expense_date,expense.supplier,expense.supplier_invoice_number),as_dict=1)
		if len(exp_rec)>0:
			frappe.throw("Please ensure that the line entries for fields Date, Supplier and Supplier Invoice in the table are not duplicate")