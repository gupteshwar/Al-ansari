frappe.ui.form.on("Blanket Order Item",{
    "qty" : function(frm,cdt,cdn){
        change_amount(frm,cdt,cdn)
    },
    "rate" : function(frm,cdt,cdn){
        change_amount(frm,cdt,cdn)
        },
});

function change_amount(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "amount", d.qty  * d.rate);
    frm.refresh_field('amount')
}

