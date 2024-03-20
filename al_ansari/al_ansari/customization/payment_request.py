import frappe
import erpnext

@frappe.whitelist()
def payment_request_validate(doc, method):
    if doc.reference_doctype=="Purchase Order" and doc.reference_name:
        if doc.grand_total<0:
            doc.grand_total = 0
            frappe.msgprint("Amount should be greater than Zero", alert=True)
        grand_total_sum = doc.grand_total
        payment_requests = frappe.db.get_all("Payment Request", filters={ 'docstatus': ['!=', '2'], 'reference_doctype': 'Purchase Order', 'reference_name': doc.reference_name, 'name': ['!=', doc.name] }, fields=['name', 'grand_total'])
        for payment_request in payment_requests:
            if payment_request.grand_total:
                grand_total_sum += payment_request.grand_total
        grand_total = frappe.db.get_value(doc.reference_doctype, doc.reference_name, 'grand_total')
        rounded_total = frappe.db.get_value(doc.reference_doctype, doc.reference_name, 'rounded_total')
        if grand_total > rounded_total:
            total = grand_total
        else:
            total = rounded_total
        if total < grand_total_sum:
            frappe.throw(title="Amount Exceeded!", msg="Sum of Payment Request amount should be less than PO amount.")