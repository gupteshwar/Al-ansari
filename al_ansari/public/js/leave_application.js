frappe.ui.form.on('Leave Application', {
	refresh: function(frm) {
		if(frm.doc.docstatus==1) {
			frm.add_custom_button(__("Mark Rejoin Details"), function() {
				var local_doc = frappe.model.get_new_doc('Rejoining Details');
			    local_doc.employee = frm.doc.employee;
			    local_doc.intial_rejoin_date = frm.doc.rejoin_date;
			    local_doc.status = 'On Leave'
			    local_doc.leave_application = frm.doc.name
			    local_doc.actual_rejoining_date = frappe.datetime.nowdate()
			    local_doc.days_difference = frappe.datetime.get_day_diff(frappe.datetime.nowdate(),frm.doc.rejoin_date)
			    frappe.set_route('Form',"Rejoining Details",local_doc.name);	
			});
		}
	},
	validate: function(frm) {
		// auto fill rejoin date field
		frm.set_value('rejoin_date',frappe.datetime.add_days(frm.doc.to_date, 1))
	}
});
