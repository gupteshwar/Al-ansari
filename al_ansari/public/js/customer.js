frappe.ui.form.on("Customer",{
    refresh:function(frm){
        cur_frm.set_query("cost_center","credit_limits",function(){
                return {
                    filters: [["company","=",frm.doc.credit_limits[0].company]]
                } 
            
        })
    },
    cr_number: function(frm) {
        if (frm.doc.cr_number) {
            var fieldname = "cr_number"
            allNumbers(frm.doc.cr_number,frm,fieldname)
        }
    }
})
function allNumbers(inputtxt,frm,fieldname)
{
 var numbers = /^[0-9]+$/;
 if(!inputtxt.match(numbers))
   {
    frm.set_value(fieldname,"")
    frappe.throw("Only Numeric values accepted")
   }
}
