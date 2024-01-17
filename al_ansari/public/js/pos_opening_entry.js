frappe.ui.form.on("POS Opening Entry",{
    after_save:function(frm){
        payment_mode(frm);
    },
})


function payment_mode(frm){
    
    (frm.doc.balance_details || []).forEach(function(payment_mode){
        if(payment_mode.mode_of_payment=="Cash"){
            frappe.msgprint("Transfer Cash To Branch")
            // frappe.throw(__("Transfer Cash To Branch"))
        }

    })
}