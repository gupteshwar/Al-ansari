frappe.ui.form.on('Stock Entry', { 
refresh:function(frm) {
	if(frm.doc.stock_entry_type == 'Goods on Approval' || frm.doc.stock_entry_type == 'Goods Return Entry'){
		var item_toggle_fields = ['s_warehouse','t_warehouse','item_code','branch','project','cost_center']
		$.each(item_toggle_fields || [], function(i, field) { frm.fields_dict.items.grid.toggle_enable(field, false); });
		var toggle_header_items = ['project','branch','cost_center']
		frm.toggle_enable(toggle_header_items,false)
	}
	else {
		var item_toggle_fields = ['s_warehouse','t_warehouse','item_code','branch','project','cost_center']
			$.each(item_toggle_fields || [], function(i, field) { frm.fields_dict.items.grid.toggle_enable(field, true); });
			var toggle_header_items = ['project','branch','cost_center']
			frm.toggle_enable(toggle_header_items,true)
	}
	},
	onload:function(frm) {
	if(frm.doc.stock_entry_type == 'Goods on Approval' || frm.doc.stock_entry_type == 'Goods Return Entry'){
			var item_toggle_fields = ['s_warehouse','t_warehouse','item_code','branch','project','cost_center']
			$.each(item_toggle_fields || [], function(i, field) { frm.fields_dict.items.grid.toggle_enable(field, false); });
			var toggle_header_items = ['project','branch','cost_center']
			frm.toggle_enable(toggle_header_items,false)
	}else {
		var item_toggle_fields = ['s_warehouse','t_warehouse','item_code','branch','project','cost_center']
		$.each(item_toggle_fields || [], function(i, field) { frm.fields_dict.items.grid.toggle_enable(field, true); });
		var toggle_header_items = ['project','branch','cost_center']
		frm.toggle_enable(toggle_header_items,true)
	}
}
})


