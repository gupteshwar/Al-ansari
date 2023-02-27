frappe.ui.form.on("Sales Order",{
    before_save : function(frm){
        item_rate(frm)
        // validate_posting_date(frm)
    },
})


function item_rate(frm){
   
        (frm.doc.items || []).forEach(function(item_rate){

            if (item_rate.rate < item_rate.price_list_rate){
                frappe.throw(__("Item rate is below price list rate"))
            }
        })
}

function validate_posting_date(frm) {
    if(frm.transaction_date){
        var currentdate = get_today()
        if (frm.transaction_date != currentdate){
            frappe.throw(__("Transaction Date should be equal to current date"))
        }
    }
    
}