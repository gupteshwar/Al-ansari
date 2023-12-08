import frappe

def validate_asset_repair(doc, method):
    if doc.repair_cost and doc.purchase_invoice:
        purchase_invoice_total = frappe.get_value("Purchase Invoice",doc.purchase_invoice,fieldname=['grand_total'])
        if doc.repair_cost < purchase_invoice_total:
            frappe.throw("Asset Repair cannot be less than the Purchase Invoice")