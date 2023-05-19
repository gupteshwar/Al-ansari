// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rejoining Details', {
	onload: function(frm) {
		frm.set_value("status","Rejoined")
		if (frm.is_new() ==1) {
			frm.set_value("lwp_application","")
		}
	},
	refresh: function(frm) {
		// filter employee field dropdown
		frm.set_query("employee", function() {
	        return {
	            "filters": {
	                "working_status": "On Leave",
	            }
	        };
	    });
		// filter leave application field dropdown
	    frm.set_query("leave_application", function() {
	        return {
	            "filters": {
	                "docstatus": 1,
	                "employee": frm.doc.employee,
	                "rejoining_doc": ""
	            }
	        };
	    });
	},
	validate: function(frm) {
		var days_difference = frappe.datetime.get_day_diff(frappe.datetime.nowdate(),frm.doc.rejoin_date)
		frm.set_value("days_difference",frappe.datetime.get_day_diff(frappe.datetime.nowdate(),frm.doc.rejoin_date))
	}
});
