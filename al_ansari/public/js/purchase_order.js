frappe.ui.form.on("Purchase Order",{
    before_save : function(frm){
        validate_posting_date(frm)
        item_rate(frm)
    },
})

function validate_posting_date(frm) {
    if(frm.transaction_date){
        var currentdate = get_today()
        if (frm.transaction_date != currentdate){
            frappe.throw(__("Transaction Date should be equal to current date"))
        }
    }
    
}

function item_rate(frm){
   
    (frm.doc.items || []).forEach(function(item_rate){

        if (item_rate.rate < item_rate.price_list_rate){
            frappe.throw(__("Item rate is below price list rate"))
        }
    })
}


frappe.ui.form.on("Purchase Order", "refresh", function(frm) {
    if (frm.doc.docstatus == 1){
    frappe.call({
        method: "al_ansari.al_ansari.doctype.consignment_tracking.consignment_tracking.get_consign_name",
        args: {
                "docname":frm.doc.name
        },
        callback: function(r){
        if (r.message){
            var po_name = (r.message['purchase_order'])
    
            if (po_name) {
                frm.remove_custom_button(__("Consignment Tracking Details"), function() {
                    frm.set_df_property("custom_button", "hidden", true);
                })
            }
        } 
        else {
            frm.add_custom_button(__("Consignment Tracking Details"), function() {
            frm.set_df_property("custom_button", "hidden", true);

                frappe.prompt([
                    {
                        label: 'Purchase Order',
                        fieldname: 'purchase_order',
                        fieldtype: 'Data',
                        default : frm.doc.name
                    },
                    {
                        label: 'Consignment',
                        fieldname: 'consignment',
                        fieldtype: 'Data'

                    },
                    {
                        label: 'Shipment Details',
                        fieldname: 'shipment_details',
                        fieldtype: 'Data'

                    },
                    {
                        label: 'Container Number',
                        fieldname: 'container_number',
                        fieldtype: 'Data'
                    },
                    {
                        label: 'Tracking Number',
                        fieldname: 'tracking_number',
                        fieldtype: 'Data'

                    },
                    {
                        label: 'Tracking Link',
                        fieldname: 'tracking_link',
                        fieldtype: 'Data'
                    },
                    {
                        label: 'Expected Arrival Date',
                        fieldname: 'expected_arrival_date',
                        fieldtype: "Date"
                    },
                ],  (values) => {
                        
                    frappe.call({
                        method:"al_ansari.al_ansari.doctype.consignment_tracking.consignment_tracking.submit_consign_tracking",
                        args : {
                            'doc':values
                        }
                    })
                })
                }, __("Create"));
                
            }    
        }
        })
    }
});