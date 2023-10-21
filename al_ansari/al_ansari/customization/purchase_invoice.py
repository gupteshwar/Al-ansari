import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.purchase_order and not i.purchase_receipt:
                i.cost_center = doc.cost_center
            elif i.purchase_order:
                purchase_order = frappe.get_doc('Purchase Order', i.purchase_order)
                for so in purchase_order.items:
                    if i.item_code == so.item_code:
                        i.cost_center = so.cost_center
            elif i.purchase_receipt:
                purchase_receipt = frappe.get_doc('Purchase Receipt', i.purchase_receipt)
                for so in purchase_receipt.items:
                    if i.item_code == so.item_code:
                        i.cost_center = so.cost_center