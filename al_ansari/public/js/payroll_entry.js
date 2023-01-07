frappe.ui.form.on('Payroll Entry', {
	refresh: function(frm) {
		if(!frm.is_new() && frm.doc.docstatus == 0) {
			// Calculate Overtime to mark additional salary entry
			frm.add_custom_button(__("Overtime Entry"), function() {
				if(frm.doc.start_date && frm.doc.end_date) {
					var local_doc = frappe.model.get_new_doc('Overtime Calculator');
				    local_doc.from_date = frm.doc.start_date;
				    local_doc.to_date = frm.doc.end_date;
				    local_doc.payroll_date = frm.doc.posting_date
				    frappe.set_route('Form',"Overtime Calculator",local_doc.name);
				} else {
					frappe.throw("Start and End dates should be selected")
				}              
			}, __("Create"));
			// check attendance to mark LWP
			if(cur_frm.doc.lwp_updated != 1 && !frm.is_new()){
				frm.add_custom_button(__("Auto Mark LWP"), function() {
					if(frm.doc.start_date && frm.doc.end_date) {
						frappe.call({
							method: "al_ansari.al_ansari.customization.leave_application.validate_to_mark_lwp",
							args: {
								"payroll_entry": frm.doc
							},
							freeze: true,
                			freeze_message: __("Marking LWP for absent records..."),
							callback: function(r) {
								if (r.message){
									console.log(r.message)
									if(r.message.length == 0) {
										frappe.msgprint("No records found to update LWPs")
									} else {
										frm.set_value('lwp_updated',1)
										frappe.msgprint("Records updated successfully")
										frm.save()
									}
								}
							}
						})
					} else {
						frappe.throw("Start and End dates should be selected")
					}               
				}, __("Create"));
			}
			
		}
	}
})

