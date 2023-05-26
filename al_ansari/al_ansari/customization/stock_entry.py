import frappe
from frappe import _

def before_submit(doc,method):
	# check the qty and validate
	validate_qty_from_goods_on_approval(doc)
	print("validate_qty_from_goods_on_approval")

def	on_submit(doc,method):
	if doc.goods_on_approval_ref:
		update_in_goods_on_approval(doc)
		update_goa_status(doc)

def validate_qty_from_goods_on_approval(doc):
	if doc.stock_entry_type == "Goods on Approval" or doc.stock_entry_type == "Goods Return Entry":
		exceeds_goa_qty = []
		exceeds_goa_i_qty = []
		
		for item in doc.items:
			
			goa_qty = frappe.db.sql("""Select sum(sed.qty) as g_qty 
				from `tabStock Entry Detail` sed,`tabGoods On Approval` goa
				where 
					sed.parent = goa.name and
					sed.item_code = %s and
					goa.name = %s
				""",(item.item_code,doc.goods_on_approval_ref),as_dict=1)
				
			if doc.stock_entry_type == 'Goods on Approval':
				goa_i_qty = frappe.db.sql("""Select sum(sed.qty) as i_qty
					from `tabStock Entry Detail` sed,`tabStock Entry` st
					where 
						sed.parent = st.name and
						sed.item_code = %s and
						st.goods_on_approval_ref = %s and
						st.docstatus in (0,1) and
						st.stock_entry_type = "Goods on Approval"
					""",(item.item_code,doc.goods_on_approval_ref),as_dict=1)

				if goa_i_qty[0]['i_qty'] > goa_qty[0]['g_qty']:
					exceeds_goa_qty.append(item.idx)
					
			if doc.stock_entry_type == 'Goods Return Entry':
				goa_i_qty = frappe.db.sql("""Select sum(sed.qty) as i_qty
					from `tabStock Entry Detail` sed,`tabStock Entry` st
					where 
						sed.parent = st.name and
						sed.item_code = %s and
						st.goods_on_approval_ref = %s and
						st.docstatus in (0,1) and
						st.stock_entry_type = "Goods on Approval"
					""",(item.item_code,doc.goods_on_approval_ref),as_dict=1)

				gra_i_qty = frappe.db.sql("""Select sum(sed.qty) as i_qty
					from `tabStock Entry Detail` sed,`tabStock Entry` st
					where 
						sed.parent = st.name and
						sed.item_code = %s and
						st.goods_on_approval_ref = %s and
						st.docstatus in (0,1) and
						st.stock_entry_type = "Goods Return Entry"
					""",(item.item_code,doc.goods_on_approval_ref),as_dict=1)

				if gra_i_qty[0]['i_qty'] > goa_qty[0]['g_qty']:
					exceeds_goa_qty.append(item.idx)
				else:
					if gra_i_qty[0]['i_qty'] > goa_i_qty[0]['i_qty']:
						exceeds_goa_i_qty.append(item.idx)
					
		if exceeds_goa_qty:
			frappe.throw(_("The quantity should not exceed the quantity in Goods On Approval Doctype ({0}) child table for row {1}").format(doc.goods_on_approval_ref, exceeds_goa_qty))
		if exceeds_goa_i_qty:
			frappe.throw(_("The quantity should not exceed the quantity in Stock Entry with Stock Entry Type as Goods on Approval for row {0}").format(exceeds_goa_i_qty))

def update_in_goods_on_approval(doc):
	items = doc.items
	stock_entry_type = doc.stock_entry_type
	goa_doc = frappe.get_doc('Goods On Approval',doc.goods_on_approval_ref)
	if goa_doc:
		for item in items:
			for goa_item in goa_doc.stock_entry_detail:
				if item.s_warehouse == goa_item.s_warehouse and item.item_code == goa_item.item_code:
					if stock_entry_type == 'Goods on Approval':
						goa_item.goods_on_approval_count += item.qty
				if item.t_warehouse == goa_item.t_warehouse and item.item_code == goa_item.item_code:	
					if stock_entry_type == 'Goods Return Entry':
						goa_item.goods_received_count += item.qty
	goa_doc.save()

def update_goa_status(doc):
	goa_doc = frappe.get_doc('Goods On Approval',doc.goods_on_approval_ref)

	# for item in goa_doc.stock_entry_detail:
	# 	if item.qty == item.goods_on_approval_count:
	# 		if item.goods_on_approval_count == item.goods_received_count and item.goods_received_count != 0:
	# 			goa_doc.status = "Goods Received"
	# 	if item.qty == item.goods_on_approval_count:
	# 		if item.goods_on_approval_count != item.goods_received_count and item.goods_received_count != 0:
	# 			goa_doc.status = "Goods Partially Received"
	# 			break
	# 	if item.qty == item.goods_on_approval_count:
	# 		if item.goods_on_approval_count != item.goods_received_count and item.goods_received_count == 0:
	# 			goa_doc.status = "Goods Sent"
	# 	if item.qty > item.goods_on_approval_count:
	# 		if item.goods_on_approval_count == item.goods_received_count and item.goods_received_count != 0:
	# 			goa_doc.status = "Goods Partially Sent"
	# 			break
	# 	if item.qty > item.goods_on_approval_count:
	# 		if item.goods_on_approval_count != item.goods_received_count and item.goods_received_count != 0:
	# 			goa_doc.status = " Goods Partially Received/Sent"
	# 			break
	item = 0
	itemwise_status = []
	while item < len(goa_doc.stock_entry_detail):
		if goa_doc.stock_entry_detail[item].goods_on_approval_count == goa_doc.stock_entry_detail[item].goods_received_count and goa_doc.stock_entry_detail[item].goods_on_approval_count == goa_doc.stock_entry_detail[item].qty:
			itemwise_status.append("Complete")
		else:
			itemwise_status.append("In Process")
		item +=1
	
	if "In Process" in itemwise_status:
		goa_doc.status = "In Process"
	else:
		goa_doc.status = "Completed"
	goa_doc.save()