import frappe

def validate_cost_center(doc, method):
    for i in doc.items:
        if doc.cost_center != i.cost_center:
            frappe.throw('Payroll cost center and items cost center should be same... ')