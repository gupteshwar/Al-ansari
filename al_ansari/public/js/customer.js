frappe.ui.form.on("Customer",{
    refresh:function(frm){
        cur_frm.set_query("cost_center","credit_limits",function(){
                return {
                    filters: [["company","=",frm.doc.credit_limits[0].company]]
                } 
            
        })
    }
})
