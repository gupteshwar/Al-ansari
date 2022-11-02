frappe.ui.form.on('Employee', {
	salary_assignment_issued: function(frm) {
		if(frm.doc.salary_assignment_issued == 1){
			frm.set_query("bank_account", function() {
				return {
					filters: {
						"party_type": "Employee",
						"party": frm.doc.name
					}
				};
			});
		}
	}
});

frappe.ui.form.on('Cost Center Change Detail', { 
	from_date: function(frm,cdt,cdn) {
		var row = locals[cdt][cdn]
		if((row.from_date && row.to_date) && (row.from_date < row.to_date)){
			row.no_of_days = frappe.datetime.get_day_diff(row.to_date, row.from_date)
			row.cost_center = frm.doc.payroll_cost_center
		} 
		frm.refresh_fields('cost_center_details')
	},
	to_date: function(frm,cdt,cdn) {
		var row = locals[cdt][cdn]
		if((row.from_date && row.to_date) && (row.from_date<row.to_date)){
			row.no_of_days = frappe.datetime.get_day_diff(row.to_date, row.from_date)
			row.cost_center = frm.doc.payroll_cost_center
		}
		frm.refresh_fields('cost_center_details')
	}
})