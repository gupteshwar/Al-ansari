import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.against_sales_order and not i.against_sales_invoice:
                i.cost_center = doc.cost_center