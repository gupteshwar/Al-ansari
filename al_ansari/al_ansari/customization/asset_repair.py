import frappe

def validate_asset_repair(doc, method):
    if doc.asset:
        assetDoc = frappe.get_doc("Asset", doc.asset)
        pi_total_amount = 0
        if assetDoc.purchase_invoice:
            pi_total_amount = frappe.get_value("Purchase Invoice", assetDoc.purchase_invoice, "grand_total")

        if doc.repair_cost > pi_total_amount and pi_total_amount != 0:
            frappe.throw("Asset Repair should Not Exceed the repair cost")