frappe.ui.form.on("Item Price List",{ 
	validate: function(frm) {
		if( frm.doc.limiting_rate && frm.doc.price_list_rate ) {
			if (frm.doc.selling == 1) {
				if(frm.doc.limiting_rate > frm.doc.price_list_rate) {
					frappe.msgprint(" The limiting rate cannot exceed the price list rate")
				}
			}
		}
	}
});