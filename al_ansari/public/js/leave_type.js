frappe.ui.form.on('Leave Type', {
	is_pplbd: function(frm) {
		if(frm.doc.is_pplbd == 0) {
			frm.set_value('partial_paid_leave','')
		}
	},
	is_lwp: function(frm) {
		if(frm.doc.is_lwp == 1) {
			frm.set_value('partial_paid_leave','')
		}
	}
});