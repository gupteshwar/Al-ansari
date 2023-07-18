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
	}
});

frappe.ui.form.on('Quotation Item', {
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
	}
});