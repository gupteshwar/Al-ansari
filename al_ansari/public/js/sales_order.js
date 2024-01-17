frappe.ui.form.on("Sales Order",{
    before_save : function(frm){
        item_rate(frm)
        // validate_posting_date(frm)
    },
    refresh: function(frm) {
        if(!frm.is_new()) {
            frappe.call({
                method: "al_ansari.al_ansari.customization.sales_order.validate_print_permissions",
                args: {
                    'doctype': frm.doc.doctype,
                    'company': frm.doc.company
                },
                callback: function(r) {
                    if (!r.exc) {
                        if (r.message == 0) {
                            cur_frm.page.menu.find('[data-label="Print"]').parent().parent().remove();
                            $("[data-original-title='Print']").hide()
                        }
                    }
                }
            })
        }
    }
})

function item_rate(frm){
    let item_rate_issue = [];
    (frm.doc.items || []).forEach(function(item){

        if (item.rate < item.limiting_rate && (item.against_blanket_order == 0)){
            item_rate_issue.push(item.idx)
        }
    })
    if (item_rate_issue.length > 0) {
        frappe.throw(__("Item Rate is below the Limiting Rate for the following rows <br>{0}",[item_rate_issue.join(',')]))
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


frappe.ui.form.on("Sales Order Item",{
    qty : function(frm,cdt,cdn){
        let row = locals[cdt][cdn]

        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Bin',
                'filters': {'item_code': row.item_code, 'warehouse':row.warehouse},
                'fieldname': [
                    'reserved_qty',
                    'reserved_qty_for_production',
                    'reserved_qty_for_sub_contract'
                ]
            },
            callback: function(r) {
                if (!r.exc) {
                    // code snippet
                    var reserved_qty = r.message.reserved_qty || 0
                    var reserved_qty_for_production = r.message.reserved_qty_for_production || 0
                    var reserved_qty_for_sub_contract = r.message.reserved_qty_for_sub_contract || 0
                    var total_reserved = reserved_qty + reserved_qty_for_production + reserved_qty_for_sub_contract || 0
                    if (total_reserved > 0) {
                        frappe.msgprint(__("Some stock is already reserved please check <br><b> Total Reserved: {0} </b> \
                        <br>Reserved Quantity: {1} <br>Reserved Qty for Production: {2} \
                        <br>Reserved Qty for Sub Contract: {3}\
                        ",[total_reserved,reserved_qty,reserved_qty_for_production,reserved_qty_for_sub_contract]))
                    } else {
                        frappe.msgprint(__("No Reserved Qty found for this item"))
                    }
                }
            }
        });
    },

    rate: function (frm,cdt,cdn) {
    //     let row = locals[cdt][cdn]
    //     frappe.call({
    //         method: 'frappe.client.get_value',
    //         args: {
    //             'doctype': 'Item Price',
    //             'filters': {'item_code': row.item_code, 'selling':1},
    //             'fieldname': [
    //                 'limiting_rate'
    //             ]
    //         },
    //         callback: function(r) {
    //             if (!r.exc) {
    //                 // code snippet
    //                 row.limiting_rate = r.message.limiting_rate
    //             }
    //         }
    //     });
        // let row = locals[cdt][cdn]
        // item_rate(frm)
    }
})