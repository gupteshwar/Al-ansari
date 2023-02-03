frappe.ui.form.on('Employee', {
	refresh: function(frm) {
		frm.set_query("payroll_cost_center", function() {
	        return {
	            "filters": {
	                "company": frm.doc.company,
	            }
	        };
	    });
	},
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
	},
	payroll_cost_center:function(frm) {
		frm.clear_table("cost_center_details")
		var childTable = cur_frm.add_child("cost_center_details");
		childTable.from_date= frappe.datetime.get_today()
		childTable.cost_center = frm.doc.payroll_cost_center
		cur_frm.refresh_fields("cost_center_details");
	},
	validate: function(frm) {
		if(frm.doc.hourly_rate) {
			frm.set_value('h_ot_rate',frm.doc.hourly_rate * frm.doc.h_ot_multiplier )
			frm.set_value('nh_ot_rate',frm.doc.hourly_rate * frm.doc.nh_ot_multiplier )

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