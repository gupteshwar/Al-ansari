frappe.ui.form.on('Expense Claim', {
	refresh: function(frm) {
		
	},
    validate: function(frm) {
        (frm.doc.expenses || []).forEach(function(d) { 
            d.cost_center = cur_frm.doc.cost_center
        })
        frm.refresh_field('expenses')
    }
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
});

frappe.ui.form.on('Expense Claim Details', {
	
});