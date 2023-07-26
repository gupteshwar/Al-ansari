from operator import itemgetter

import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate
from six import iteritems

import erpnext
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition
from erpnext.stock.utils import add_additional_uom_columns, is_reposting_item_valuation_in_progress


def get_data(data):
	return {
		"fieldname": "prevdoc_docname",
		"non_standard_fieldnames": {
			"Auto Repeat": "reference_document",
		},
		"transactions": [
			{"label": _("Sales Order"), "items": ["Sales Order"]},
			{"label": _("Subscription"), "items": ["Auto Repeat"]},
            {"label": "", "items": ["Credit Application"]},
		],
	}

@frappe.whitelist(allow_guest=True)
def get_item_stock_details(item, transaction_date, company, warehouse=None):
    print(warehouse)
    query = []
    warehouse = frappe.db.sql("""
                    select 
                        name
                    from    
                        `tabWarehouse`
                """, as_dict=1)
    
    for i in warehouse:
        data = []
        data.append(i.name)
        actual_qty = frappe.db.sql("""
                        select 
                            coalesce(sum(actual_qty), 0) as qty
                        from 
                            `tabStock Ledger Entry` 
                        where 
                            item_code='{item}'
                            and warehouse='{warehouse}'
                            and company = '{company}'
                            and posting_date <= CURDATE()
                    """.format(item=item, warehouse=i.name, company=company, date=transaction_date))
       
        data.append(actual_qty[0][0])
        if actual_qty[0][0] == 0:
            continue
        po = frappe.db.sql("""
                select
                    coalesce(sum((po_item.qty - po_item.received_qty)*po_item.conversion_factor), 0) as po_qty
                from 
                    `tabPurchase Order Item` po_item, 
                    `tabPurchase Order` po
                where 
                    po_item.item_code='{item}' 
                    and po_item.warehouse='{warehouse}'
                    and po.company = '{company}'
                    and po.transaction_date <= CURDATE()
                    and po_item.qty > po_item.received_qty 
                    and po_item.parent=po.name
                    and po.status not in ('Closed', 'Delivered') 
                    and po.docstatus=1
                    and po_item.delivered_by_supplier = 0
                """.format(item=item, warehouse=i.name, company=company))
        
        data.append(po[0][0])
        so = frappe.db.sql("""
                select 
                    coalesce(sum(so_item.qty - so_item.delivered_qty), 0) as so_qty
                from
                    `tabSales Order Item` so_item,
                    `tabSales Order` so
                where
                    so_item.item_code='{item}' 
                    and so_item.warehouse='{warehouse}'
                    and so.company = '{company}'
                    and so.transaction_date <= CURDATE()
                    and so_item.parent=so.name 
                    and so.docstatus=1
                """.format(item=item, warehouse=i.name, company=company))
       
        data.append(so[0][0])
        material_receipt = 0
        material_receipt_ = frappe.db.sql("""
                            select
                                coalesce((sed.qty), 0) as qty
                            from
                                `tabStock Entry` se,
                                `tabStock Entry Detail` sed 
                            where
                                sed.parent = se.name
                                and sed.item_code = '{item}' 
                                and sed.t_warehouse='{warehouse}'
                                and se.company = '{company}'
                                and se.docstatus = 0
                                and se.stock_entry_type = 'Material Receipt'
                            """.format(item=item, warehouse=i.name, company=company))
        print(material_receipt_)
        if material_receipt_:
            material_receipt = material_receipt_[0][0]

        material_issue = 0
        material_issue_ = frappe.db.sql("""
                            select 
                                coalesce((sed.qty), 0) as qty
                            from
                                `tabStock Entry` se,
                                `tabStock Entry Detail` sed 
                            where
                                sed.parent = se.name
                                and sed.item_code = '{item}' 
                                and sed.s_warehouse='{warehouse}'
                                and se.company = '{company}'
                                and se.docstatus = 0
                                and se.stock_entry_type = 'Material Issue'
                            """.format(item=item, warehouse=i.name, company=company))
        print(material_issue_)
        if material_issue_:
            material_issue = material_issue_[0][0]

        material_transfer_add = 0
        material_transfer_add_ = frappe.db.sql("""
                            select 
                                coalesce((sed.qty), 0) as qty
                            from
                                `tabStock Entry` se,
                                `tabStock Entry Detail` sed 
                            where
                                sed.parent = se.name
                                and sed.item_code = '{item}' 
                                and sed.t_warehouse='{warehouse}'
                                and se.company = '{company}'
                                and se.docstatus = 0
                                and se.stock_entry_type = 'Material Transfer'
                            """.format(item=item, warehouse=i.name, company=company))
        
        if material_transfer_add_:
            material_transfer_add = material_transfer_add_[0][0]

        material_transfer_sub = 0
        material_transfer_sub_ = frappe.db.sql("""
                            select 
                                coalesce((sed.qty), 0) as qty
                            from
                                `tabStock Entry` se,
                                `tabStock Entry Detail` sed 
                            where
                                sed.parent = se.name
                                and sed.item_code = '{item}' 
                                and sed.s_warehouse='{warehouse}'
                                and se.company = '{company}'
                                and se.docstatus = 0
                                and se.stock_entry_type = 'Material Transfer'
                            """.format(item=item, warehouse=i.name, company=company))
       
        if material_transfer_sub_:
            material_transfer_sub = material_transfer_sub_[0][0]

        materials_qty = material_receipt - material_issue
        
        total_materials_qty = materials_qty
        
        if material_transfer_add:
            total_materials_qty = materials_qty + material_transfer_add
        
        if material_transfer_sub:
            total_materials_qty = materials_qty - material_transfer_sub
        
        data.append(total_materials_qty)
       
        data.append((actual_qty[0][0]+po[0][0]-so[0][0]-total_materials_qty))
        
        query.append(data)
   

    data_to_show = ""
    header = f'''<div class="wrapper" style="overflow:scroll;width:100%;">
                <center><h3>Item Stock Details</h3></center><br>
                <table class="table table-bordered" style="width:100%">
                <tr>
                    <th>Warehouse</th>
                    <th>Total Stock In Warehouse</th>
                    <th>Pending PO</th>
                    <th>Projected Stock After Purchase</th>
                    <th>Pending SO Delivery</th>
                    <th>Pending Transfer</th>
                    <th>Available Net Quantity</th>
                </tr>'''

    for row in query:
        data_to_show = data_to_show + '''<tr>
                                            <td>{warehouse}</td>
                                            <td>{total_stock} </td>
                                            <td>{pending_po}</td>
                                            <td>{project_stock} </td>
                                            <td>{pending_so}</td>
                                            <td>{pending_transfered}</td>
                                            <td>{total_qty}</td>
                                        </tr>'''.format(warehouse = row[0], 
                                                        total_stock = row[1],
                                                        pending_po = row[2],
                                                        project_stock = row[1]+row[2],
                                                        pending_so = row[3], 
                                                        pending_transfered = row[4],
                                                        total_qty = row[5]
                                        )

    data_to_show = data_to_show + '''</table> </div>'''
    frappe.msgprint(header+data_to_show)