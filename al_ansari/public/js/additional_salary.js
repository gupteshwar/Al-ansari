frappe.ui.form.on('Additional Salary', { 
	validate: function(frm) {
		frappe.call({
	        method: "frappe.client.get_value",
	        args: {
	                doctype: "Additional Salary",
	                fieldname: "name",
	                filters: {
	                	employee: frm.doc.employee,
						payroll_date: frm.doc.payroll_date,
	                }
	        },
	        callback: function(response) {
	             var name = response.message.name;
	             console.log("response.message="+response.message.name)
	             if (name) {
	                  frappe.msgprint("Record for same time period already exists");
				validated=false;
	    			return false;
			
	             }
	        }
		});
	}
})