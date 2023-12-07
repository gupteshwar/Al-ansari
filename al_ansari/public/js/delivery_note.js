frappe.ui.form.on('Delivery Note',{
    onload: function(frm) {
        var hasLinkedSalesOrder = false;
        $.each(frm.doc.items || [], function (i, item) {
            if (item.against_sales_order) {
                hasLinkedSalesOrder = true;
                return false;
            }
        });
        if(hasLinkedSalesOrder = true) {
            $('*[data-fieldname="items"]').find('.grid-download').hide();
            $('*[data-fieldname="items"]').find('.grid-upload').hide(); 
        } else {
            $('*[data-fieldname="items"]').find('.grid-download').show();
            $('*[data-fieldname="items"]').find('.grid-upload').show();
        }
        
        frm.get_field('items').grid.cannot_add_rows = hasLinkedSalesOrder;
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