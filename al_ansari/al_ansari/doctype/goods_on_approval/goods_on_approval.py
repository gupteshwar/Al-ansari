# Copyright (c) 2023, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.get_item_details import (
	get_bin_details,
	get_conversion_factor,
	get_default_cost_center,
	get_reserved_qty_for_so,
)
from frappe.utils import nowdate
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.setup.doctype.brand.brand import get_brand_defaults


class GoodsOnApproval(Document):
	# pass

	@frappe.whitelist()
	def get_item_details(self, args=None, for_update=False):
		item = frappe.db.sql(
			"""select i.name, i.stock_uom, i.description, i.image, i.item_name, i.item_group,
				i.has_batch_no, i.sample_quantity, i.has_serial_no, i.allow_alternative_item,
				id.expense_account, id.buying_cost_center
			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
			where i.name=%s
				and i.disabled=0
				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
			(self.company, args.get("item_code"), nowdate()),
			as_dict=1,
		)

		if not item:
			frappe.throw(
				_("Item {0} is not active or end of life has been reached").format(args.get("item_code"))
			)

		item = item[0]
		item_group_defaults = get_item_group_defaults(item.name, self.company)
		brand_defaults = get_brand_defaults(item.name, self.company)

		ret = frappe._dict(
			{
				"uom": item.stock_uom,
				"stock_uom": item.stock_uom,
				"description": item.description,
				"image": item.image,
				"item_name": item.item_name,
				"cost_center": get_default_cost_center(
					args, item, item_group_defaults, brand_defaults, self.company
				),
				"qty": args.get("qty"),
				"transfer_qty": args.get("qty"),
				"conversion_factor": 1,
				"batch_no": "",
				"actual_qty": 0,
				"basic_rate": 0,
				"serial_no": "",
				"has_serial_no": item.has_serial_no,
				"has_batch_no": item.has_batch_no,
				"sample_quantity": item.sample_quantity,
				"expense_account": item.expense_account,
			}
		)

		# if self.purpose == "Send to Subcontractor":
		# 	ret["allow_alternative_item"] = item.allow_alternative_item

		# update uom
		if args.get("uom") and for_update:
			ret.update(get_uom_details(args.get("item_code"), args.get("uom"), args.get("qty")))

		# if self.purpose == "Material Issue":
		# 	ret["expense_account"] = (
		# 		item.get("expense_account")
		# 		or item_group_defaults.get("expense_account")
		# 		or frappe.get_cached_value("Company", self.company, "default_expense_account")
		# 	)

		for company_field, field in {
			"stock_adjustment_account": "expense_account",
			"cost_center": "cost_center",
		}.items():
			if not ret.get(field):
				ret[field] = frappe.get_cached_value("Company", self.company, company_field)

		args["posting_date"] = self.posting_date
		# args["posting_time"] = self.posting_time

		# stock_and_rate = get_warehouse_details(args) if args.get("warehouse") else {}
		# ret.update(stock_and_rate)

		# automatically select batch for outgoing item
		# if (
		# 	args.get("s_warehouse", None)
		# 	and args.get("qty")
		# 	and ret.get("has_batch_no")
		# 	and not args.get("batch_no")
		# ):
		# 	args.batch_no = get_batch_no(args["item_code"], args["s_warehouse"], args["qty"])

		# if (
		# 	self.purpose == "Send to Subcontractor" and self.get("purchase_order") and args.get("item_code")
		# ):
		# 	subcontract_items = frappe.get_all(
		# 		"Purchase Order Item Supplied",
		# 		{"parent": self.purchase_order, "rm_item_code": args.get("item_code")},
		# 		"main_item_code",
		# 	)

		# 	if subcontract_items and len(subcontract_items) == 1:
		# 		ret["subcontracted_item"] = subcontract_items[0].main_item_code

		return ret

def create_entry_goa(doc,method=None):
	goa_doc = frappe.new_doc("Goods On Approval")
	goa_doc_child = frappe.new_doc("Stock Entry Detail")
	for i in doc.items:
		print(i)
	# frappe.throw("sjk")
	goa_doc.save()