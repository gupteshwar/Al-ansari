// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Earned Leave Deductions', {
	get_applicants: function(frm) {
		// fetch applicants from the attendance doctype whose status is 'On leave' or 'Absent'
		 frappe.call({
            method: "al_ansari.al_ansari.doctype.earned_leave_deductions.earned_leave_deductions.get_applicants", //dotted path to server method
            args: {
            	"frm" : frm.doc
            },
            callback: function(r) {
                // code snippet
                console.log(r.message)
                for(var j=0; j<r.message.length;j++){
                	var childTable = cur_frm.add_child("deduction_ratio");
                	childTable.employee_id= r.message[j].employee
                	childTable.employee_name = r.message[j].employee_name
                	childTable.no_of_lwp = r.message[j].no_of_lwp
                	childTable.el_allocated = r.message[j].el_allocated
                	childTable.no_of_working_days = 22
                	childTable.deduction_ratio = r.message[j].deduction_ratio
                	childTable.to_be_deducted = r.message[j].to_be_deducted
                	childTable.to_be_allocated = r.message[j].to_be_allocated
                	cur_frm.refresh_fields("deduction_ratio");
                }
            }
        })
	}
});