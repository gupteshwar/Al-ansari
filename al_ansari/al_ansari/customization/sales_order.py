import frappe

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

