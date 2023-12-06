frappe.ui.form.on("Sales Invoice",{
    refresh:function(frm){
        cur_frm.set_query("accessory_item","items",function(){
            return {
                filters: [['is_accessory',"=",1]]
            }
        })
    },
    before_save:function(frm) {
        // validate_posting_date(frm)   
    },

    onload: function(frm) {

        var hasLinkedSalesOrder = false;
        $.each(frm.doc.items || [], function (i, item) {
            if (item.sales_order) {
                hasLinkedSalesOrder = true;
                return false;
            }
        });

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

function validate_posting_date(frm) {
    if(frm.posting_date){
        var currentdate = get_today()
        if (frm.posting_date!=currentdate){
            frappe.throw(__("Posting Date should be equal to current date"))
        }
    }
    
}


frappe.ui.form.on("Sales Invoice", "is_return", function (frm, cdt, cdn) {
   if(frm.doc.is_return == 1){
            frm.set_value('update_stock', 1);
   }
});



