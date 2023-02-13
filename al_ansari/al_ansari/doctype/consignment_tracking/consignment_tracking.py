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
	print(doc['shipment_details'])
	consign_doc = frappe.get_doc({
				"doctype":"Consignment Tracking",
				"purchase_order":doc['purchase_order'],
				'consignment': doc['consignment'],
				"shipment_details":doc['shipment_details'],
				"container_number":doc['container_number'],
				"tracking_number":doc['tracking_number'],
				"tracking_link":doc['tracking_link'],
				"expected_arrival_date":doc['expected_arrival_date']
			})
	consign_doc.save(ignore_permissions=True)

