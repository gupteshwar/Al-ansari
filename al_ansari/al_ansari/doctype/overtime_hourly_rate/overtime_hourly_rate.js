// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Hourly Rate', {
	// refresh: function(frm) {

	// }
	employee_grade: function(frm) {
		// fetch basic from salary assignment for all employees
		// Overtime Hourly Rate (Basic/Hours Base * Multipler)
		frappe.call({
			method:"al_ansari.al_ansari.doctype.overtime_hourly_rate.overtime_hourly_rate.get_hourly_rate_details",
	        args:{
	        	"grade":frm.doc.employee_grade
	        },
	        callback: function(r) { 
	        	console.log(r.message)
	        	// add rows in child table
	        	if(r.message.length >=0){
	        		console.log(r.message.length)
	        		for(var i=0;i<r.message.length;i++){
	        			var childTable = cur_frm.add_child("overtime_hourly_rate");
	        			childTable.employee=r.message[i].name
	        			childTable.employee_name=r.message[i].employee_name
	        			childTable.hourly_rate=(r.message[i].base*(frm.doc.multiplier||1))/(frm.doc.hours_base||1)
	        			cur_frm.refresh_fields("overtime_hourly_rate");
	        		}
	        	}
	        	
	        }
	    })
	}
});

