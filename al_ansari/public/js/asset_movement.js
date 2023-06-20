frappe.ui.form.on('Asset Movement', { 
    // filter for To Cost Center in Assets Child table
    refresh: function(frm){
        frm.set_query('to_cost_center', 'assets', () => {
            return {
                filters:[
                    ['Cost Center', 'company', '=', frm.doc.company],
                    ['Cost Center', 'is_group', '=', 0],
                    ['Cost Center', 'disabled', '=', 0],

                ]
            }
        })
    }
})