// Copyright (c) 2023, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consignment Tracking', {
	refresh: function(frm) {
		
		frm.add_custom_button(__("Purchase Receipt"), function(){
			frappe.model.open_mapped_doc({
				method: "al_ansari.al_ansari.doctype.consignment_tracking.consignment_tracking.make_purchase_receipt",
				frm: cur_frm,
				freeze_message: __("Creating Purchase Receipt ...")
			})
		},_("Create"))
		
	}
});
