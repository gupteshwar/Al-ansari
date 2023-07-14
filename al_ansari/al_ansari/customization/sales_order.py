import frappe
import json

def before_save(doc,method):
    validate_item_qty(doc,method)

def on_submit(doc,method):
    update_sales_details(doc,method)
   
def validate_item_qty(doc,method):
    total_qty = 0
    remaining_qty = 0
    for i in doc.items:
        if i.blanket_order:
            blank_doc = frappe.get_doc("Blanket Order",i.blanket_order)
            for j in blank_doc.items:
                if i.item_code == j.item_code:
                    total_qty += i.qty
                    
                remaining_qty = j.qty - j.ordered_qty
                exceeds_qty = i.qty - remaining_qty
                if total_qty > remaining_qty:
                    frappe.throw(f"Sales Order exceeds Blanket Order by {exceeds_qty}")

def update_sales_details(doc,method):
    for i in doc.items:
        if i.blanket_order:
            blank_doc = frappe.get_doc("Blanket Order",i.blanket_order)
    
            blank_doc.append('sales_details',{
                'sales_order':doc.name,
                'grand_total':doc.grand_total
            })
            blank_doc.save()


@frappe.whitelist()
def validation_for_duplicate_PR_in_landed_cost_voucher(doc):
    doc = json.loads(doc)

    purchase_receipts = doc['purchase_receipts'] 
    valid_pr = []
    new_doc = 0
    try:
        if doc['__islocal']:
            new_doc = 1
    except:
        new_doc = 0

    if new_doc == 1:
        for i in range(len(purchase_receipts)):
            r = frappe.db.sql(""" Select parent from `tabLanded Cost Purchase Receipt`
                where receipt_document_type = %s
                and receipt_document = %s
                """,(purchase_receipts[i]['receipt_document_type'],purchase_receipts[i]['receipt_document']),as_dict=1)
            if not r:
                valid_pr.append(doc['purchase_receipts'][i]['receipt_document'])
    elif new_doc == 0:
        for j in range(len(purchase_receipts)):
            r = frappe.db.sql(""" Select parent from `tabLanded Cost Purchase Receipt`
                where receipt_document_type = %s
                and receipt_document = %s
                """,(purchase_receipts[j]['receipt_document_type'],purchase_receipts[j]['receipt_document']),as_dict=1)
            if not r:
                valid_pr.append(purchase_receipts[j]['receipt_document'])
            elif r:
                if r[0]['parent'] == doc['parent']:
                    valid_pr.append(purchase_receipts[j]['receipt_document'])
    return valid_pr

@frappe.whitelist()
def validate_print_permissions(doctype, company):
    print_settings = frappe.db.get_all('Custom Print Settings Details', 
                    filters={'company': company, 'document': doctype}, fields=
                    ['draft_print'])
    
    if print_settings:
        return print_settings[0]['draft_print']