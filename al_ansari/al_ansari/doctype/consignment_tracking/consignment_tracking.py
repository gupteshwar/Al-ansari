# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt

class ConsignmentTracking(Document):
	pass

@frappe.whitelist()
def submit_consign_tracking(doc):
	doc = json.loads(doc)
	print(doc['purchase_order_reference'])  
	items_data = frappe.get_doc("Purchase Order", doc['purchase_order_reference'])
      	
	print(items_data.items)  
	consign_doc = frappe.get_doc({
	"doctype":"Consignment Tracking",
	"purchase_order_reference":doc['purchase_order_reference'],
	"shipper":doc['shipper'],
	"shipper_name":doc['shipper_name'],
	"type_of_shipment":doc['type_of_shipment'],
	"container_number":doc['container_number'],
	"actual_date_of_shipment":doc['actual_date_of_shipment'],
	"expected_arrival_date":doc['expected_arrival_date'],
	})
	consign_doc.save(ignore_permissions=True)
	consign_doc.items = items_data.items
	consign_doc.save(ignore_permissions=True)

	return consign_doc	

@frappe.whitelist()
def get_consign_name(docname):
    if docname:
        consign_name = frappe.db.get_value("Consignment Tracking",{"purchase_order":docname},'name')
    if consign_name:
        consign_doc = frappe.get_doc("Consignment Tracking",consign_name)
        return consign_doc

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	consignment_doc = frappe.get_doc("Consignment Tracking", source_name)
	def update_item(obj, target, source_parent):
		po_doc = frappe.get_doc("Purchase Order", consignment_doc.purchase_order_reference)
		target.qty = flt(obj.qty) - flt(obj.received_qty)
		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (
			(flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(po_doc.conversion_rate)
		)

	doc = get_mapped_doc(
		"Consignment Tracking",
		source_name,
		{
			"Consignment Tracking": {
				"doctype": "Purchase Receipt",
				"field_map": {
					"shipper": "supplier",
					"shipper_name": "supplier_name",
					"supplier_warehouse": "supplier_warehouse"
					},
				# "validation": {
				# 	"docstatus": ["=", 1],
				# },
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"name": "purchase_order_item",
					"parent": "consignment_tracking",
					"bom": "bom",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
				},
				"postprocess": update_item,
				"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
				and doc.delivered_by_supplier != 1,
			},
			"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
	)

	doc.set_onload("ignore_price_list", True)

	return doc

def set_missing_values(source, target):
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")
