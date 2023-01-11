frappe.ui.form.on('Additional Salary', { 
	refresh: function(frm) {
		frm.set_query("salary_component", function() {
	        return {
	            "filters": {
	            	"company":frm.doc.company,
	                "restrict_manual_entry": 0,
	            }
	        };
	    });
	},
	employee: function(frm) {
		frm.set_query("salary_component", function() {
	        return {
	            "filters": {
	            	"company":frm.doc.company,
	                "restrict_manual_entry": 0,
	            }
	        };
	    });
	},
	validate: function(frm) {
		frappe.call({
	        method: "frappe.client.get_value",
	        args: {
	                doctype: "Additional Salary",
	                fieldname: "name",
	                filters: {
	                	employee: frm.doc.employee,
						payroll_date: frm.doc.payroll_date,
						salary_component: 'Overtime'
	                }
	        },
	        callback: function(response) {
	             var name = response.message.name;
	             console.log("response.message="+response.message.name)
	             if (name) {
	                  frappe.msgprint("Overtime entry for same payroll date already exists for the employee selected");
				validated=false;
	    			return false;
	             }
	        }
		});
	}
})