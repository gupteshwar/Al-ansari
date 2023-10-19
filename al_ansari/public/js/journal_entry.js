frappe.ui.form.on('Journal Entry', {
    before_save:function(frm){
        // validate_posting_date(frm)
        split_cost_center_wise_account_entries(frm)
    },
    onload: function(frm) {
        if (frappe.session.user) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: {
                        user_id: frappe.session.user
                    },
                    fieldname: 'payroll_cost_center'
                },
                callback: function(response) {
                    if (response.message) {

                        if(frm.doc.__islocal && !frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                        }
                        else if(!frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                            // frm.save()
                        }
                    }
                }
            });
        }
    }

})

frappe.ui.form.on('Journal Entry Account', {
    accounts_add: function(frm,cdt,cdn) {
        let row = locals[cdt][cdn];
        row.cost_center = frm.doc.cost_center
        row.branch = frm.doc.branch
        row.project = frm.doc.project
        frm.refresh_field('accounts');

    },
    account:  function(frm,cdt,cdn) {
        let row = locals[cdt][cdn];
        row.cost_center = frm.doc.cost_center
        row.branch = frm.doc.branch
        row.project = frm.doc.project
        frm.refresh_field("accounts")
    }
})

function validate_posting_date(frm) {
    if(frm.posting_date){
        var currentdate = get_today()
        if (frm.posting_date != currentdate){
            frappe.throw(__("Posting Date should be equal to current date"))
        }
    }
    
}

function split_cost_center_wise_account_entries(frm) {
    if (frm.doc.accounts) {
        frm.clear_table("cc_accounting_entries")
        frappe.call({
            method: "al_ansari.al_ansari.customization.utils.fetch_cr_dr_details",
            args: {
                doc: frm.doc
            },
            callback(r) {
                console.log(r)
                if (r.message) {
                    r.message.forEach(function(r){
                        var childTable = cur_frm.add_child("cc_accounting_entries");
                        childTable.cost_center = r.cost_center
                        childTable.debit = r.debit
                        childTable.credit = r.credit
                        childTable.total_difference = r.debit - r.credit
                    })
                    cur_frm.refresh_fields("cc_accounting_entries");    
                }
            }
        })
    }
}