import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.sales_order:
                i.cost_center = doc.cost_center