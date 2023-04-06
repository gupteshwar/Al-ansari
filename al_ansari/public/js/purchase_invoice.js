frappe.ui.form.on('Purchase Invoice',{
    before_save:function (frm) {
        // validate_posting_date(frm)
    }

})

function validate_posting_date(frm) {
    if(frm.posting_date){
        var currentdate = get_today()
        if (frm.posting_date!=currentdate){
            frappe.throw(__("Posting Date should be equal to current date"))
        }
    }
    
}