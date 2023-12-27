frappe.ui.form.on('Quotation', { 
	validate: function(frm) {
		if(frm.doc.quotation_to == "Customer") {
			frappe.call({
		        method: "frappe.client.get_value",
		        args: {
		                doctype: "Customer",
		                fieldname: "type_of_customer",
		                filters: {
		                	name: frm.doc.party_name
		                }
		        },
		        callback: function(response) {
		             var name = response.message.type_of_customer;
		             console.log("response.message="+response.message.type_of_customer)
		             frm.set_value('type_of_customer',response.message.type_of_customer)
		        }
			});
		}
	},
	before_save : function(frm){
        // validate_posting_date(frm)
        item_rate(frm)
    },
    cost_center: function(frm) {
        frm.doc.items.forEach(function(item){
            item.cost_center = frm.doc.cost_center
            item.branches = frm.doc.branch
        });
        frm.refresh_field('items')
    },
    branch: function(frm) {
        frm.doc.items.forEach(function(item){
            item.cost_center = frm.doc.cost_center
            item.branches = frm.doc.branch
        });
        frm.refresh_field('items')
    },
});

function item_rate(frm){
    let item_rate_issue = [];
    (frm.doc.items || []).forEach(function(item){

        if (item.rate < item.limiting_rate){
            item_rate_issue.push(item.idx)
        }
    })
    if (item_rate_issue.length > 0) {
        frappe.throw(__("Item Rate is below Limiting Rate for the following rows <br>{0}",[item_rate_issue.join(',')]))
    }
}

frappe.ui.form.on('Quotation Item', {
	item_code: function(frm,cdt,cdn) {
		var d = locals[cdt][cdn];
        d.delivery_date = frm.doc.valid_till;
	},
	item_enquiry: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if(row.item_code) {
			frappe.call({
				method: "al_ansari.al_ansari.customization.quotation.get_item_stock_details",
				args: {
					item:row.item_code,
					warehouse: row.warehouse,
					transaction_date: frm.doc.transaction_date,
					company: frm.doc.company
				},
				callback: function(r) {
					console.log(r)
				}
			})
		}
	},
	rate: function(frm,cdt,cdn) {
		var d = locals[cdt][cdn]
		item_rate(frm)
	}
});