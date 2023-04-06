import frappe

def validate_paid_amt_greater_than_outstanding_amt(doc,method):
    if doc.references:
        total_outstanding = 0
        for i in doc.references:
            total_outstanding = total_outstanding + i.outstanding_amount
        if  total_outstanding < doc.paid_amount :
                frappe.throw(title="Amount Exceeded!", msg="Paid amount is greater than the Outstanding amount")