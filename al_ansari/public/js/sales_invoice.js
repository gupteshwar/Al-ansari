frappe.ui.form.on("Sales Invoice",{
    onload:function(frm){
        cur_frm.set_query("accessory_item","items",function(){
            return {
                filters: [['is_accessory',"=",1]]
            }
        })
    },
    before_save:function(frm) {
        validate_posting_date(frm)   
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





