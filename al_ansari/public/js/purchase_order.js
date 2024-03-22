frappe.ui.form.on("Purchase Order",{
    before_save : function(frm){
        // validate_posting_date(frm)
        item_rate(frm)
    },
    // cost_center: function(frm) {
    //     frm.doc.items.forEach(function(item){
    //         item.cost_center = frm.doc.cost_center
    //         item.branches = frm.doc.branch
    //     });
    //     frm.refresh_field('items')
    // },
    branch: function(frm) {
        frm.doc.items.forEach(function(item){
            item.cost_center = frm.doc.cost_center
            item.branches = frm.doc.branch
        });
        frm.refresh_field('items')
    },
    onload_post_render:function(frm) {
        if(frm.is_new() && frm.doc.supplier) {
            frappe.call({
                method: 'frappe.client.get_value',
                    args: {
                        'doctype': 'Supplier',
                        'filters': {'name': frm.doc.supplier},
                        'fieldname': [
                            'type_of_entity'
                        ]
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            // code snippet
                            frm.set_value('type_of_entity',r.message.type_of_entity)
                        }
                    }
            })
        }
    },

    // 123_onload: function(frm) {
    //     // payroll_cost_center

    // },
        
    // Commented the auto fill of payroll cost center

    // onload: function(frm) {
    //     if (frappe.session.user) {
    //         frappe.call({
    //             method: 'frappe.client.get_value',
    //             args: {
    //                 doctype: 'Employee',
    //                 filters: {
    //                     user_id: frappe.session.user
    //                 },
    //                 fieldname: 'payroll_cost_center'
    //             },
    //             callback: function(response) {
    //                 if (response.message) {

    //                     if(frm.doc.__islocal && !frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                     }
    //                     else if(!frm.doc.cost_center){
    //                         frm.set_value('cost_center', response.message.payroll_cost_center);
    //                         // frm.save()
    //                     }
    //                 }
    //             }
    //         });
    //     }
    // }
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
        let item_rate_issue = [];
        (frm.doc.items || []).forEach(function(item){

            if (item.rate > item.limiting_rate){
                item_rate_issue.push(item.idx)
            }
        })
        if (item_rate_issue.length > 0) {
            frappe.throw(__("Item Rate should not exceed Limiting List Rate for the following rows <br>{0}",[item_rate_issue.join(',')]))
        }
}


frappe.ui.form.on("Purchase Order", "refresh", function(frm) {
    if (frm.doc.docstatus == 1){
        frm.add_custom_button(__("Consignment Tracking Details"), function() {
            
            let d = new frappe.ui.Dialog({
                title: 'Consignment Entry',
                fields: [
                    {
                        label: 'Purchase Order',
                        fieldname: 'purchase_order_reference',
                        fieldtype: 'Data',
                        default : frm.doc.name,
                        read_only:1
                    },
                    {
                        label: 'Shipper',
                        fieldname: 'shipper',
                        fieldtype: 'Link',
                        default: frm.doc.supplier,
                        read_only:1
                    },
                    {
                        label: 'Shipper Name',
                        fieldname: 'shipper_name',
                        fieldtype: 'Data',
                        default: frm.doc.supplier_name,
                        read_only:1
                    },
                    {
                        label: 'Type of Shipment',
                        fieldname: 'type_of_shipment',
                        fieldtype: 'Link',
                        options: "Type of Shipment",
                        reqd:1
                    },
                    {
                        label: '',
                        fieldname: 'col_break_1',
                        fieldtype: 'Column Break'

                    },
                    {
                        label: 'Container Number',
                        fieldname: 'container_number',
                        fieldtype: 'Data',
                        reqd:1
                    },
                    {
                        label:'Actual Date of Shipment',
                        fieldname: 'actual_date_of_shipment',
                        fieldtype: 'Date',
                        reqd:1
                    },
                    {
                        label: 'Expected Arrival Date',
                        fieldname: 'expected_arrival_date',
                        fieldtype: "Date",
                        reqd:1
                    },
                ],
                size: 'large', // small, large, extra-large 
                primary_action_label: 'Submit',
                primary_action(values) {
                    // console.log(values);
                    frappe.call({
                        method:"al_ansari.al_ansari.doctype.consignment_tracking.consignment_tracking.submit_consign_tracking",
                        args : {
                            'doc':values
                        },
                        callback: function(r) {
                            if(r.message){
                                frappe.msgprint(__("Consignment created {0}",[r.message.name]))
                            }
                        }
                    })
                    d.hide();
                }
            });

        d.show();
        }, __("Create"));
                
    }
});
