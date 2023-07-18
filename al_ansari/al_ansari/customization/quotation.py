from operator import itemgetter

import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate
from six import iteritems

import erpnext
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition
from erpnext.stock.utils import add_additional_uom_columns, is_reposting_item_valuation_in_progress

@frappe.whitelist(allow_guest=True)
def get_item_stock_details(item, warehouse, transaction_date):
    query = []
    warehouse = frappe.db.sql("""
                    select 
                        name
                    from    
                        `tabWarehouse`
                """, as_dict=1)
    
    for i in warehouse:
        a = []
        a.append(i.name)
        actual_qty = frappe.db.sql("""
                        select 
                            coalesce(sum(actual_qty), 0) as qty
                        from 
                            `tabStock Ledger Entry` 
                        where 
                            item_code='{item}'
                            and warehouse='{warehouse}';
                    """.format(item=item, warehouse=i.name))
        
        a.append(actual_qty[0][0])

        po = frappe.db.sql("""
                select
                    coalesce(sum((po_item.qty - po_item.received_qty)*po_item.conversion_factor), 0) as po_qty
                from 
                    `tabPurchase Order Item` po_item, 
                    `tabPurchase Order` po
                where 
                    po_item.item_code='{item}' and po_item.warehouse='{warehouse}'
                    and po_item.qty > po_item.received_qty and po_item.parent=po.name
                    and po.status not in ('Closed', 'Delivered') and po.docstatus=1
                    and po_item.delivered_by_supplier = 0
                """.format(item=item, warehouse=i.name))
        print('po', po)
        a.append(po[0][0])
        so = frappe.db.sql("""
                select 
                    coalesce(sum(so_item.qty - so_item.delivered_qty), 0) as so_qty
                from
                    `tabSales Order Item` so_item,
                    `tabSales Order` so
                where
                    so_item.item_code='{item}' and so_item.warehouse='{warehouse}'
                    and so_item.parent=so.name and so.docstatus=1
                """)
        print('so', so)
        a.append(so[0][0])
        a.append(actual_qty[0][0]-(po[0][0]+so[0][0]))
        query.append(a)
   

    data_to_show = ""
    header = f'''<div class="wrapper" style="width:100%;">
                <center><h3>Item Stock Details</h3></center><br>
                <table class="table table-bordered" style="width:100%">
                <tr>
                    <th>Warehouse</th>
                    <th>Total stock</th>
                    <th>Pending PO</th>
                    <th>Pending SO Delivery</th>
                    <th>Pending Transfer</th>
                    <th>Available Quantity</th>
                </tr>'''

    for row in query:
        data_to_show = data_to_show + '''<tr>
                                            <td>{warehouse}</td>
                                            <td>{total_stock} </td>
                                            <td>{pending_po}</td>
                                            <td>{pending_so}</td>
                                            <td></td>
                                            <td>{total_qty}</td>
                                        </tr>'''.format(warehouse = row[0], 
                                                        total_stock = row[1], 
                                                        pending_po = row[2], 
                                                        pending_so = row[3], 
                                                        total_qty = row[4]
                                        )

    data_to_show = data_to_show + '''</table> </div>'''
    frappe.msgprint(header+data_to_show)