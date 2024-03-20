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
    },
    transaction_date: function(frm) {
        if(frm.doc.transaction_date) {
            frappe.call({
            args: {
                "asset_movement": frm.doc,
            },
            method: "erpnext.assets.doctype.asset_movement.asset_movement.fetch_asset_cost_center_as_per_date",
            callback: function(r) {
                for(var i=0;i<r.message[0].length;i++){
                    for(var j=0;j<frm.doc.assets.length;j++){
                        if (r.message[0][i]['asset'] == frm.doc.assets[j]['asset']){
                            frm.doc.assets[j]['from_cost_center'] = r.message[0][i]['from_cost_center']
                        }
                    }
                }
                frm.refresh_field('assets')
            }
        });
        }
    }
})