frappe.ui.form.on('Leave Application', {
	refresh: function(frm) {
		// Rejoining Details button should be visible only on Annual Leave application
		if(frm.doc.docstatus==1 && !frm.doc.rejoining_details_ref && frm.doc.leave_type == 'Annual Leave') {
			frm.add_custom_button(__("Mark Rejoin Details"), function() {
				frappe.call({
					method: "al_ansari.al_ansari.doctype.rejoining_details.rejoining_details.validate_rejoining_record",
					args: {
						"leave": frm.doc,
					},
					callback: function(r) {
						if (r.message){
							var doclist = frappe.model.sync(r.message);
							frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
						}
					}
				})
			});
			
		}
	},
	validate: function(frm) {
		// auto fill rejoin date field
		frm.set_value('rejoin_date',frappe.datetime.add_days(frm.doc.to_date, 1))
	}
});
