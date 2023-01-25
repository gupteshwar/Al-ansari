frappe.ui.form.on('Salary Slip', { 
	refresh: function(frm) {
		frm.set_df_property("earnings", "read_only", 1);
		frm.set_df_property("deductions", "read_only", 1);
	}
})

