frappe.provide("erpnext.accounts.dimensions");
frappe.ui.form.on('Payroll Entry', {
	refresh: function(frm) {
		if(!frm.is_new() && frm.doc.docstatus == 0) {
			// Calculate Overtime to mark additional salary entry
			frm.add_custom_button(__("Overtime Entry"), function() {
				if(frm.doc.start_date && frm.doc.end_date) {
					// var local_doc = frappe.model.get_new_doc('Overtime Calculator');
				    // local_doc.from_date = frm.doc.start_date;
				    // local_doc.to_date = frm.doc.end_date;
				    // local_doc.payroll_date = frm.doc.posting_date
				    // frappe.set_route('Form',"Overtime Calculator",local_doc.name);
				    frappe.call({
    					method: "al_ansari.al_ansari.doctype.overtime_calculator.overtime_calculator.autofill_employees",
    					args: {
							"payroll_entry": frm.doc
						},
    					callback: function(r) {
    						if (r.message){
    							var doclist = frappe.model.sync(r.message);
    							frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
    						}
    					}
    				})
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
									frm.set_value('lwp_updated',1)
									frm.save()
									frappe.show_alert("Records updated successfully",6)
								}
							}
						})
					} else {
						frappe.throw("Start and End dates should be selected")
					}               
				}, __("Create"));

			}

		}

		frm.set_query("payroll_cost_center", function() {
	        return {
	            "filters": {
	                "company": frm.doc.company,
	            }
	        };
	    });

		frm.set_query("partial_entry", function() {
	        return {
	            "filters": {
	                "docstatus": 0,
	            }
	        };
	    });
	},
	on_submit: function(frm) {
		frappe.set_route("Form","Payroll Entry",frm.doc.payroll_entry)
	},
	validate: function(frm) {
		if(frm.doc.payroll_cost_center != frm.doc.cost_center) {
			frappe.throw(__("The values selected for Payroll Cost Center and Cost Center should match"))
		}
		if(frm.doc.lwp_updated == 1) {
			frappe.call({
				method: "al_ansari.al_ansari.customization.leave_application.validate_if_lwp_are_marked",
				args: {
					"frm":frm.doc
				},
				callback: function(r) {
					console.log(r.message)
					if(r.message.length>0){
						frappe.msgprint(__("Please check note the following records couldn't be updated for LWPs <br>{0}",[r.message.join(",")]))
						frappe.validated = false
					}
				}
			})
		}
	},
    // Commented the auto fill of payroll cost center
	
	// onload: function(frm) {
    //     if (frappe.session.user) {
    //         frappe.call({
    //             method: 'frappe.client.get_value',
    //             args: {
    //                 doctype: 'Employee',
    //                 filters: {
    //                     user_id: frappe.session.user
    //                 },
    //                 fieldname: 'payroll_cost_center'
    //             },
    //             callback: function(response) {
    //                 if (response.message) {

    //                     if(frm.doc.__islocal && !frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                     }
    //                     else if(!frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                         // frm.save()
    //                     }
    //                 }
    //             }
    //         });
    //     }
    // }
})