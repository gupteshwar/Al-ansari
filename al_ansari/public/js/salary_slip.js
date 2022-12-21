frappe.ui.form.on('Salary Slip', { 
	onload: function(frm) {
		frm.get_field('earnings').grid.cannot_add_rows = true;
		frm.get_field('deductions').grid.cannot_add_rows = true;
	},
	refresh: function(frm) {
		frm.get_field('earnings').grid.cannot_add_rows = true;
		frm.get_field('deductions').grid.cannot_add_rows = true;	
	}
})

