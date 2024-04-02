import frappe
import json
from frappe import _

def before_save(doc,method):
    validate_item_qty(doc,method)
    issue_item = []
    for item in doc.items:
        if item.rate < item.limiting_rate:
            issue_item.append(item.idx)
    if issue_item:
        frappe.throw(_("IItem Rate cannot be below the Limiting Rate for the following rows <br>{0}").format(issue_item))

def on_submit(doc,method):
    update_sales_details(doc,method)
   
def validate_item_qty(doc,method):
    
    for i in doc.items:
        if i.blanket_order:
            total_qty = 0
            remaining_qty = 0
            blank_doc = frappe.get_doc("Blanket Order",i.blanket_order)
            for j in blank_doc.items:
                if i.item_code == j.item_code:
                    total_qty += i.qty
                    remaining_qty = j.qty - j.ordered_qty
                    exceeds_qty = remaining_qty-i.qty
                    if total_qty > remaining_qty:
                        frappe.throw(f"Sales Order exceeds Blanket Order by {abs(exceeds_qty)} in row {i.idx}")
                    if i.rate != j.rate:
                        frappe.throw(f"The item rate in Sales Order should match the item Rate in Blanket Order for row {i.idx}")


def update_sales_details(doc,method):
    blanket_order_list = []
    for i in doc.items:
        if i.blanket_order and (i.blanket_order not in blanket_order_list):
            blanket_order_list.append(i.blanket_order) 
    for blanket_order in blanket_order_list:
        blank_doc = frappe.get_doc("Blanket Order",blanket_order)

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

def validate_cost_center(doc, method):
    if doc.cost_center:
        for i in doc.items:
            if not i.cost_center:

                i.cost_center = doc.cost_center

