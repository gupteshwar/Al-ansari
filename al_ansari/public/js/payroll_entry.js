frappe.ui.form.on('Payroll Entry', {
	refresh: function(frm) {
		if(!frm.is_new() && frm.doc.docstatus != 1) {
			frm.add_custom_button(__("Calculate Overtime"), function() {
				if(frm.doc.start_date && frm.doc.end_date) {
					var local_doc = frappe.model.get_new_doc('Overtime Calculator');
				    local_doc.from_date = frm.doc.start_date;
				    local_doc.to_date = frm.doc.end_date;
				    local_doc.payroll_date = frm.doc.posting_date
				    frappe.set_route('Form',"Overtime Calculator",local_doc.name);
				} else {
					frappe.throw("Start and End dates should be selected")
				}       
			        
			});
		}
	}
})

