frappe.ui.form.on("Sales Order",{
    before_save : function(frm){
        item_rate(frm)
        // validate_posting_date(frm)
    },
    on_submit: function(frm){
        if(frm.doc.docstatus ==1){
            blanket_order_details(frm)
        }
    }
})


function item_rate(frm){
   
        (frm.doc.items || []).forEach(function(item_rate){

            if (item_rate.rate < item_rate.price_list_rate){
                frappe.throw(__("Item rate is below price list rate"))
            }
        })
}

function blanket_order_details(frm){
    if (frm.doc.items["0"].blanket_order){
      
        var blanket_order = frm.doc.items["0"].blanket_order
        var bo_doc = frappe.model.get_doc("Blanket Order", blanket_order)
        console.log(bo_doc)
        $.each(bo_doc.items, function(index, row){  
            var d = bo_doc.add_child("sales_details");
                d.name = frm.doc.name
                d.grand_total = frm.doc.grand_total
        })
    }

}

function validate_posting_date(frm) {
    if(frm.transaction_date){
        var currentdate = get_today()
        if (frm.transaction_date != currentdate){
            frappe.throw(__("Transaction Date should be equal to current date"))
        }
    }
    
}