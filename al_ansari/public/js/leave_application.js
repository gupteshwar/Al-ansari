frappe.ui.form.on('Leave Application', {
	refresh: function(frm) {
		// if(frm.doc.employee){
		// 	// fetch grade from employee record
		// 	frappe.call({
		// 	    method: 'frappe.client.get_value',
		// 	    args: {
		// 	        'doctype': 'Employee',
		// 	        'filters': {'name': frm.doc.employee},
		// 	        'fieldname': [
		// 	            'grade'
		// 	        ]
		// 	    },
		// 	    callback: function(r) {
		// 	        if (!r.exc) {
		// 	            set_filter_on_leave_type(frm,r.message.grade)
		// 	        }
		// 	    }
		// 	});
		// }
	},
	employee:function(frm) {
		// if(frm.doc.employee){
		// 	// fetch grade from employee record
		// 	frappe.call({
		// 	    method: 'frappe.client.get_value',
		// 	    args: {
		// 	        'doctype': 'Employee',
		// 	        'filters': {'name': frm.doc.employee},
		// 	        'fieldname': [
		// 	            'grade'
		// 	        ]
		// 	    },
		// 	    callback: function(r) {
		// 	        if (!r.exc) {
		// 	            set_filter_on_leave_type(frm,r.message.grade)
		// 	        }
		// 	    }
		// 	});
		// }
	}
});

var set_filter_on_leave_type = function(frm,grade){
	// set filters for leave type based on grade
	frm.set_query("leave_type", function() {
	    return {
	        "filters": {
	            "employee_grade": grade,
	            // "leave_type_name": "Leave Without Pay"
	        }
	    };
	});

}