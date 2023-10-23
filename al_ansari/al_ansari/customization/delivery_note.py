import frappe

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.against_sales_order and not i.against_sales_invoice:
                i.cost_center = doc.cost_center
            elif i.against_sales_order:
                sales_order = frappe.get_doc('Sales Order', i.against_sales_order)
                for so in sales_order.items:
                    if i.item_code == so.item_code and i.idx and so.idx:
                        i.cost_center = so.cost_center
            elif i.against_sales_invoice:
                sales_invoice = frappe.get_doc('Sales Invoice', i.against_sales_invoice)
                for so in sales_invoice.items:
                    if i.item_code == so.item_code and i.idx and so.idx:
                        i.cost_center = so.cost_center