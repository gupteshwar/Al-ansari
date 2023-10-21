import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            i.cost_center = doc.cost_center