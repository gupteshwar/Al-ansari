frappe.ui.form.on('Purchase Receipt',{
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
        // var df = frappe.meta.get_docfield("Purchase Order Item","rate", cur_frm.doc.name);
        // df.read_only = 1;
        var event =""

        hide_child_table_buttons(frm)
    },

    onload: function(frm) {
        if (frappe.session.user) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: {
                        user_id: frappe.session.user
                    },
                    fieldname: 'payroll_cost_center'
                },
                callback: function(response) {
                    if (response.message) {

                        if(frm.doc.__islocal && !frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                        }
                        else if(!frm.doc.cost_center){
                            frm.set_value('cost_center', response.message.payroll_cost_center);
                            // frm.save()
                        }
                    }
                }
            });
        }
        var event =""

        hide_child_table_buttons(frm)
    },

    refresh: function(frm) {
        var event =""
        hide_child_table_buttons(event,frm)
        frm.get_field('items').grid.cannot_add_rows = true;
    }
})

frappe.ui.form.on('Purchase Receipt Item', {
    form_render(frm, cdt, cdn){
        var row = locals[cdt][cdn]
        if (row.purchase_order || row.purchase_invoice){
            frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-append-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
            // frm.fields_dict.items.grid.wrapper.find('.clear-fix').prop('disabled','true')
        }    
    },

    rate(frm,cdt,cdn) {
        var row = locals[cdt][cdn]
        if (row.purchase_order || row.purchase_invoice){
            var event = 'rate'
            hide_child_table_buttons(event,frm)
            frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-append-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
        }  
    }
});

function hide_child_table_buttons(event,frm) {
    if(frm.doc.items) {

        if(frm.doc.items[0].purchase_order || frm.doc.items[0].purchase_invoice){
            if (event != 'rate'){
                frm.fields_dict.items.grid.update_docfield_property("rate", "read_only", 1);

            }

            $('*[data-fieldname="items"]').find('.grid-remove-rows').hide();
            console.log("1")
            $('*[data-fieldname="items"]').find('.grid-add-multiple-rows').hide();
            console.log("2")
            $('*[data-fieldname="items"]').find('.grid-add-row').hide();
            console.log("3")
            $('*[data-fieldname="items"]').find('.grid-download').hide();
            console.log("4")
            $('*[data-fieldname="items"]').find('.grid-upload').hide();
            console.log("5")
            
            console.log("6")
        }
        // frm.get_field('items').grid.cannot_add_rows = true;
        // frm.get_field('items').grid.cannot_add_rows = true;
    }
}