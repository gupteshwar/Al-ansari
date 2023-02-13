frappe.ui.form.on("Request for Quotation",{

        onload: function(frm,cdt,cdn) {
            if (frm.doc.quotation){
            get_quotation_items(frm)
            }
    },
    quotation: function(frm,cdt,cdn) {
        get_quotation_items(frm)      
},
})



function get_quotation_items(frm){
    frappe.model.with_doc("Quotation", frm.doc.quotation, function() {
        console.log("innnn")
        var quot_doc= frappe.model.get_doc("Quotation", frm.doc.quotation)
        
        frm.doc.items = []
        $.each(quot_doc.items, function(index, row){   
                var d = frm.add_child("items");
                d.item_code = row.item_code,
                d.item_name = row.item_name,
                d.description = row.description,
                d.qty = row.qty,
                d.uom = row.uom,
                d.warehouse = row.warehouse,
                d.conversion_factor = row.conversion_factor,
                d.stock_qty = row.stock_qty 
            refresh_field("items");
        });
        frm.refresh()
    })
}



// frappe.ui.form.on("Request for Quotation Item",{
//     "onload": function(frm,cdt,cdn) {
//         frappe.model.with_doc("Quotation", frm.doc.quotation, function() {
//             console.log(frm.doc.quotation)
//             var clone= frappe.model.get_doc("Quotation", frm.doc.quotation)
//             var rfq_items = local[cdt][cdn];
//             // frm.doc.items = []
//                 $.each(clone.items || [], function(i, v) {
//                     frappe.model.set_value(rfq_items.doctype, rfq_items.name, "item_code",v.item_code)
//                     // frappe.model.set_value(v.doctype, v.name, "email", r.message.email)
//                     // frappe.model.set_value(v.doctype, v.name, "phone", r.message.phone)
//                 })
//                 frm.refresh_field('items');
            
//         })
//     }
// })

//

