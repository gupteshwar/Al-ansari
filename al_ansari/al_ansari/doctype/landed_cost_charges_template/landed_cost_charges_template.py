# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LandedCostChargesTemplate(Document):
	pass


@frappe.whitelist()
def get_template_items(landed_cost_charges):
	charges = frappe.get_doc("Landed Cost Charges Template",landed_cost_charges)
	return charges.landed_cost_charges