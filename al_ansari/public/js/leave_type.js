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
	},
	validate: function(frm) {
		var frequency = 0
		var rounding = 0
		if(frm.doc.is_earned_leave == 1) {
			if(frm.doc.earned_leave_frequency == 'Monthly') {
				frequency = 12
			} else if(frm.doc.earned_leave_frequency == 'Quarterly') {
				frequency = 4
			} else if(frm.doc.earned_leave_frequency == 'Half-Yearly') {
				frequency = 6
			} else if(frm.doc.earned_leave_frequency == 'Yearly') {
				frequency = 1
			}
			if(frm.doc.rounding == "0.25") {
				frm.set_value('monthly_allocation',(Math.round((frm.doc.max_leaves_allowed/frequency)*4)/4))
			} else if (frm.doc.rounding == "0.5") {
				frm.set_value('monthly_allocation',(Math.round((frm.doc.max_leaves_allowed/frequency)*2)/2))
			} else {
				frm.set_value('monthly_allocation',Math.round(frm.doc.max_leaves_allowed/frequency))
			}
			
		}
	}
});