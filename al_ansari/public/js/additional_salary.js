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
						salary_component: 'OVERTIME',
						docstatus:1
	                }
	        },
	        callback: function(response) {
	             var name = response.message.name || "";
	             // console.log("response.message="+name)
	             if (name) {
	                frappe.msgprint("Overtime entry for same payroll date already exists for the employee selected");
					frappe.validated=false;
	    			return false;
	             }
	        }
		});
	}
})