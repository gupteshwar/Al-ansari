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