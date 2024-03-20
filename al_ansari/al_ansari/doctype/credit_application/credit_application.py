# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class CreditApplication(Document):
	def on_submit(self):
		if self.docstatus == 1:
			frappe.db.set_value("Customer",self.customer,"type_of_customer","Credit")
			frappe.msgprint(_("The customer type for {0} is updated successfully to Credit").format(self.customer))