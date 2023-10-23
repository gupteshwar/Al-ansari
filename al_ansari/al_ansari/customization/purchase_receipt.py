import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.material_request and not i.purchase_order and not i.purchase_invoice:
                i.cost_center = doc.cost_center
            elif i.purchase_order:
                print('in elif')
                purchase_order = frappe.get_doc('Purchase Order', i.purchase_order)
                for so in purchase_order.items:
                    if i.item_code == so.item_code and i.idx == so.idx:
                        i.cost_center = so.cost_center
            elif i.purchase_invoice:
                purchase_invoice = frappe.get_doc('Purchase Order', i.purchase_invoice)
                for so in purchase_invoice.items:
                    if i.item_code == so.item_code and i.idx == so.idx:
                        i.cost_center = so.cost_center
