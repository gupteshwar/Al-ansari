frappe.ui.form.on('Journal Entry', {
    before_save:function(frm){
        validate_posting_date(frm)
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