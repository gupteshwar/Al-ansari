# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class ConsignmentTracking(Document):
	pass

@frappe.whitelist()
def submit_consign_tracking(doc):
	doc = json.loads(doc)
	consign_doc = frappe.get_doc({
				"doctype":"Consignment Tracking",
				"purchase_order_reference":doc['purchase_order_reference'],
				"shipper":doc['shipper'],
				"shipper_name":doc['shipper_name'],
				"type_of_shipment":doc['type_of_shipment'],
				"container_number":doc['container_number'],
				"actual_date_of_shipment":doc['actual_date_of_shipment'],
				"expected_arrival_date":doc['expected_arrival_date']
			})
	consign_doc.save(ignore_permissions=True)
	return consign_doc

@frappe.whitelist()
def get_consign_name(docname):
    if docname:
        consign_name = frappe.db.get_value("Consignment Tracking",{"purchase_order":docname},'name')
    if consign_name:
        consign_doc = frappe.get_doc("Consignment Tracking",consign_name)
        return consign_doc
