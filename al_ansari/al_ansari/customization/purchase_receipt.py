import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.material_request and not i.purchase_order and not i.purchase_invoice:
                i.cost_center = doc.cost_center