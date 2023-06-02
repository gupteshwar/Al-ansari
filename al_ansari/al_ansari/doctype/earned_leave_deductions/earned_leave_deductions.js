// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Earned Leave Deductions', {
    refresh: function(frm) {
        
    },
    from_date: function(frm) {
        if(frm.doc.from_date) {
            frm.set_value('to_date',moment(frm.doc.from_date).endOf('month').format('YYYY-MM-DD'))
        }
        if((frm.doc.from_date && frm.doc.to_date)&&(frm.doc.from_date > frm.doc.to_date)) {
            frappe.throw(" 'From date' cannot be greater than 'To Date' ")
        }
    },
    to_date: function(frm) {
        if((frm.doc.from_date && frm.doc.to_date)&&(frm.doc.from_date > frm.doc.to_date)) {
            frappe.throw(" 'From date' cannot be greater than 'To Date' ")
        }
    },
	get_employees: function(frm) {
        if(!frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw("From Date and To Date should be selected to fetch Employee Records")
        }
        
        frm.clear_table("deduction_ratio")
        frm.refresh_fields("deduction_ratio");
        frappe.call({
            doc: frm.doc,
            method: 'get_applicants',
        }).then(r => {
            if(r.message)
            for(var j=0; j<r.message.length;j++){
                 var childTable = cur_frm.add_child("deduction_ratio");
                 childTable.employee_id= r.message[j].employee
                 childTable.employee_name = r.message[j].employee_name
                 cur_frm.refresh_fields("deduction_ratio");
            }
        });
	},
    validate: function(frm) {
        if(!frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw("From Date and To Date should be selected to fetch Employee Records")
        }
        if(frm.doc.from_date > frm.doc.to_date) {
            frappe.throw(" 'From date' cannot be greater than 'To Date' ")
        }
        if(frm.doc.deduction_ratio && frm.doc.deduction_ratio.length <=0) {
            frappe.throw("No records found in the Deduction Ratio table so cannot be saved")
        } else if (!frm.doc.deduction_ratio) {
            frappe.throw("To save the records Deduction Ratio table should have atleast one entry. Try clicking the the 'Get Employees' button and then save.")
        }
        frappe.call({
            method: "al_ansari.al_ansari.doctype.earned_leave_deductions.earned_leave_deductions.no_of_working_days_employeewise", //dotted path to server method
            args: {
                "frm" : frm.doc
            },
            callback: function(r) {
                // code snippet
                console.log(r.message)
                if(r.message.length == frm.doc.deduction_ratio.length) {
                    for(var j=0; j<frm.doc.deduction_ratio.length;j++){
                    // var childTable = cur_frm.add_child("deduction_ratio");
                        if(frm.doc.deduction_ratio[j].employee_id == r.message[j].employee) {
                            frm.doc.deduction_ratio[j].no_of_working_days= r.message[j].no_of_working_days
                            frm.doc.deduction_ratio[j].el_allocated= r.message[j].el_allocated
                            frm.doc.deduction_ratio[j].allocation_from_date= r.message[j].allocation_from_date
                            frm.doc.deduction_ratio[j].allocation_end_date= r.message[j].allocation_end_date
                            frm.doc.deduction_ratio[j].no_of_lwp= r.message[j].no_of_lwp
                            frm.doc.deduction_ratio[j].days_of_month= r.message[j].days_of_month
                            frm.doc.deduction_ratio[j].deduction_ratio = frm.doc.deduction_ratio[j].el_allocated/frm.doc.deduction_ratio[j].days_of_month
                            frm.doc.deduction_ratio[j].to_be_deducted = (frm.doc.deduction_ratio[j].el_allocated/frm.doc.deduction_ratio[j].days_of_month) * frm.doc.deduction_ratio[j].no_of_lwp 
                            frm.doc.deduction_ratio[j].to_be_allocated = (frm.doc.deduction_ratio[j].el_allocated - ((frm.doc.deduction_ratio[j].el_allocated/frm.doc.deduction_ratio[j].days_of_month) * frm.doc.deduction_ratio[j].no_of_lwp))
                            cur_frm.refresh_fields("deduction_ratio");
                        }
                    }
                }
                
            }
        })
    }
});