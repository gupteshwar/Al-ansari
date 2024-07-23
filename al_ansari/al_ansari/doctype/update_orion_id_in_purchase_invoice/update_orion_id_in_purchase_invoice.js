// Copyright (c) 2024, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Update Orion ID in Purchase Invoice', {
	refresh: function(frm) {
		console.log('**********')
	},
	update_data:function(frm){
		console.log('uuuuuuuuuuuuuuuuu')
		frappe.call({
		    method: "al_ansari.al_ansari.doctype.update_orion_id_in_purchase_invoice.update_orion_id_in_purchase_invoice.update_data",
		    args:{file_path:frm.doc.attach_document},
		    callback: function (r) {
		    	alert('success')
		    },
		  });
	}
});
