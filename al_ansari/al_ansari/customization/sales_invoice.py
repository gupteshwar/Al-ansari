import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.sales_order:
                i.cost_center = doc.cost_center
            else:
                sales_order = frappe.get_doc('Sales Order', i.sales_order)
                for so in sales_order.items:
                    if i.item_code == so.item_code and i.idx == so.idx:
                        i.cost_center = so.cost_center