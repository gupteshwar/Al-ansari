frappe.ui.form.on('Purchase Invoice',{
    before_save:function (frm) {
        // validate_posting_date(frm)
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

        var event =""

        hide_child_table_buttons(event,frm)
    },
    onload: function(frm) {
        if(frappe.user.has_role("Accounts Manager") || frappe.user.has_role("System Manager")){
            frm.set_df_property('set_posting_time', 'read_only', 0)
        }else{
            frm.set_df_property('set_posting_time', 'read_only', 1)
        }
        // Commented the auto fill of payroll cost center

        // if (frappe.session.user) {
        //     frappe.call({
        //         method: 'frappe.client.get_value',
        //         args: {
        //             doctype: 'Employee',
        //             filters: {
        //                 user_id: frappe.session.user
        //             },
        //             fieldname: 'payroll_cost_center'
        //         },
        //         callback: function(response) {
        //             if (response.message) {

        //                 if(frm.doc.__islocal && !frm.doc.cost_center){
        //                     frm.set_value('cost_center', response.message.payroll_cost_center);
        //                 }
        //                 else if(!frm.doc.cost_center){
        //                     frm.set_value('cost_center', response.message.payroll_cost_center);
        //                     // frm.save()
        //                 }
        //             }
        //         }
        //     });
        // }

        var event =""

        // hide_child_table_buttons(event,frm
    },

     refresh: function(frm) {
        var event =""
        hide_child_table_buttons(event,frm)
        frm.refresh_field('items')

        if(frm.doc.is_linked_to_asset == 1 && frm.doc.asset) {
            frm.set_query("asset_repair", function() {
                return {
                    "filters": {
                        "company": frm.doc.company,
                        "asset": frm.doc.asset,
                        "docstatus": 0
                    }
                };
            });
        }
    },

    is_linked_to_asset: function (frm) {
        if(frm.doc.is_linked_to_asset == 0){
            frm.set_value('asset','')
            frm.set_value('asset_repair','')
            frm.set_value('asset_cost_center','')
        }
    },

    asset: function(frm) {
        if(frm.doc.is_linked_to_asset == 1 && frm.doc.asset){
            frm.set_query("asset_repair", function() {
                return {
                    "filters": {
                        "company": frm.doc.company,
                        "asset": frm.doc.asset,
                        "docstatus":0
                    }
                };
            });
        }
    }

})

frappe.ui.form.on('Purchase Invoice Item', {
    form_render(frm, cdt, cdn){
        var row = locals[cdt][cdn]
        if (row.purchase_order || row.purchase_receipt){
            frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        }    
    },

    rate(frm,cdt,cdn) {
        var row = locals[cdt][cdn]
        if (row.purchase_order || row.purchase_receipt){
            var event = 'rate'
            hide_child_table_buttons(event,frm)
            frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        }  
    }
});

function validate_posting_date(frm) {
    if(frm.posting_date){
        var currentdate = get_today()
        if (frm.posting_date!=currentdate){
            frappe.throw(__("Posting Date should be equal to current date"))
        }
    }
    
}

function hide_child_table_buttons(event,frm) {
    if(frm.doc.items) {
        var hasLinkedReferenceOrder = false
        $.each(frm.doc.items || [], function (i, item) {
            if(item.purchase_order || item.purchase_receipt){
                hasLinkedReferenceOrder = true
            }
        });
        if(hasLinkedReferenceOrder == true) {
            if (event != 'rate'){
                frm.fields_dict.items.grid.update_docfield_property("rate", "read_only", 1);
            }

            $('*[data-fieldname="items"]').find('.grid-download').hide();
            $('*[data-fieldname="items"]').find('.grid-upload').hide();
            frm.get_field('items').grid.cannot_add_rows = true
            
        }
    }
}