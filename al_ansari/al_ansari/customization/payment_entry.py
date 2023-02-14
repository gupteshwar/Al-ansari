import frappe

def validate_paid_amt_greater_than_outstanding_amt(doc,method):
    if doc.references:
        for i in doc.references:
            if  i.outstanding_amount > doc.paid_amount :
                frappe.throw("Outstanding amount is greater than paid amount")