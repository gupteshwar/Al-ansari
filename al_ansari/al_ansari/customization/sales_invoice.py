import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.sales_order and not i.delivery_note:
                i.cost_center = doc.cost_center
            elif i.sales_order and not i.delivery_note:
                sales_order = frappe.get_doc('Sales Order', i.sales_order)
                for so in sales_order.items:
                    if i.item_code == so.item_code and i.idx == so.idx:
                        i.cost_center = so.cost_center
            elif not i.sales_order and i.delivery_note:
                delivery_note = frappe.get_doc('Delivery Note', i.delivery_note)
                for dn in sales_order.items:
                    if i.item_code == dn.item_code and i.idx == dn.idx:
                        i.cost_center = dn.cost_center
            elif i.sales_order and i.delivery_note:
                delivery_note = frappe.get_doc('Delivery Note', i.delivery_note)
                for dn in sales_order.items:
                    if i.item_code == dn.item_code and i.idx == dn.idx:
                        i.cost_center = dn.cost_center