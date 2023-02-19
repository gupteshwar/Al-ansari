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