# Copyright (c) 2024, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import pandas as pd
from urllib.request import Request, urlopen

class UpdateOrionIDinPurchaseInvoice(Document):
	pass


@frappe.whitelist(allow_guest = True)
def update_data(file_path):
	url = frappe.utils.get_url()
	file_path = file_path.replace(" ", "%20")
	data = url + file_path

	latest_record = frappe.db.sql("""SELECT file_url from `tabFile` where attached_to_doctype = 'Update Orion ID in Purchase Invoice' order by creation desc limit 1""", as_list=1)

	if not latest_record:
		return
	else:
		data = pd.read_csv((latest_record[0][0]).replace(" ", "%20"))
		df = pd.DataFrame(data)
		for i, row in df.iterrows():
			if frappe.db.exists('Purchase Invoice', row['ID']):
				get_doc = frappe.get_doc('Purchase Invoice', row['ID'])
				get_doc.db_set("orion_reference_id", row['Orion Reference ID'])
			else:
				pass
		frappe.db.commit()