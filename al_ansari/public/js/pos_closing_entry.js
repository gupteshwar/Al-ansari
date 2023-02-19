frappe.ui.form.on("POS Closing Entry",{
    after_save:function(frm){
        payment_mode(frm);
    },
})
// frappe.ui.form.on("POS Payment Method",{
//     mode_of_payment:function(frm){
//         payment_mode(frm);
//     },
// })

function payment_mode(frm){
    (frm.doc.payment_reconciliation || []).forEach(function(payment_mode){
        if(payment_mode.mode_of_payment=="Cash" && payment_mode.closing_amount > 0){
            frappe.msgprint("Transfer Cash To Branch")
            // frappe.throw(__("Transfer Cash To Branch"))
        }

    })
}
