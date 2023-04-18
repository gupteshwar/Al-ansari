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

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        if source.company_address:
            target.update({"company_address": source.company_address})
        else:
            # set company address
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

    def update_item(source, target, source_parent):
        target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
        target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
        target.qty = flt(source.qty) - flt(source.delivered_qty)

        item = get_item_defaults(target.item_code, source_parent.company)
        item_group = get_item_group_defaults(target.item_code, source_parent.company)

        if item:
            target.cost_center = source.cost_center or (
                frappe.db.get_value("Project", source_parent.project, "cost_center")
                or item.get("buying_cost_center")
                or item_group.get("buying_cost_center")
            )

    mapper = {
        "Sales Order": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
        "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
        "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
    }

    if not skip_item_mapping:

        def condition(doc):
            # make_mapped_doc sets js `args` into `frappe.flags.args`
            if frappe.flags.args and frappe.flags.args.delivery_dates:
                if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
                    return False
            return abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier != 1

        mapper["Sales Order Item"] = {
            "doctype": "Delivery Note Item",
            "field_map": {
                "rate": "rate",
                "name": "so_detail",
                "parent": "against_sales_order",
            },
            "postprocess": update_item,
            "condition": condition,
        }

    target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)

    target_doc.set_onload("ignore_price_list", True)

    return target_doc