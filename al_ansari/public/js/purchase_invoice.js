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
    }

})

function validate_posting_date(frm) {
    if(frm.posting_date){
        var currentdate = get_today()
        if (frm.posting_date!=currentdate){
            frappe.throw(__("Posting Date should be equal to current date"))
        }
    }
    
}