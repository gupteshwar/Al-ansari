
frappe.ui.form.on('Landed Cost Voucher', {
	onload: function(frm) {
		if (frm.doc.percentage_based == 1) {
			frm.set_df_property('distribute_charges_based_on','read_only',1)
		} else {
			frm.set_df_property('distribute_charges_based_on','read_only',0)
		}
	},
	percentage_based: function(frm) {
		if (frm.doc.percentage_based == 1) {
			frm.set_value("distribute_charges_based_on","Distribute Manually")
			frm.set_df_property('distribute_charges_based_on','read_only',1)
		} else {
			frm.set_df_property('distribute_charges_based_on','read_only',0)
		}
	}, 
	landed_cost_charges_template: function(frm) {
		// add charges as per the template selected
		frm.clear_table("taxes")
		cur_frm.refresh_fields("taxes");
		if(frm.doc.landed_cost_charges_template) {
			frappe.call('al_ansari.al_ansari.doctype.landed_cost_charges_template.landed_cost_charges_template.get_template_items', {
			    landed_cost_charges: frm.doc.landed_cost_charges_template
			}).then(r => {
			    console.log(r.message)
			    for(var i=0;i<r.message.length;i++){
			    	var row = cur_frm.add_child("taxes");
			    	row.expense_account = r.message[i].expense_account
			    	row.description = r.message[i].description
			    	row.account_currency = r.message[i].account_currency
			    	row.exchange_rate = r.message[i].exchange_rate
			    	row.amount = r.message[i].amount
			    	row.base_amount = r.message[i].base_amount
			    	cur_frm.refresh_fields("taxes");
			    }

			    if (frm.doc.taxes.length >0) {
					var tax_total = 0
					for (var k=0;k<frm.doc.taxes.length;k++) {
						tax_total = tax_total + frm.doc.taxes[k].amount
					}
					frm.set_value("total_taxes_and_charges",tax_total)
					// distribute_charges(frm)
				}
			})
		}	
	},
	validate: function(frm) {
		// print("validate")
		if (frm.doc.taxes.length >0 && frm.doc.percentage_based == 1) {
			var tax_total = 0
			for (var k=0;k<frm.doc.taxes.length;k++) {
				tax_total = tax_total + frm.doc.taxes[k].amount
			}
			frm.set_value("total_taxes_and_charges",tax_total)
			if (frm.doc.total_taxes_and_charges>0)
				distribute_charges(frm)
			else
				frappe.throw(__("The Total Taxes and Charges cannot be 0.00"))
		}
	}	
})

function distribute_charges(frm) {
	if (frm.doc.percentage_based == 1 && frm.doc.distribute_charges_based_on == "Distribute Manually") {
		if(frm.doc.total_taxes_and_charges && frm.doc.taxes.length >0) {
			var percent_total = 0
			for (var j=0;j<frm.doc.items.length;j++) {
				frm.doc.items[j].applicable_charges = frm.doc.total_taxes_and_charges * flt(frm.doc.items[j].percentage/100)
				percent_total = percent_total + frm.doc.items[j].percentage
			}
			frm.refresh_fields('items')
			if (percent_total != 100) {
				frappe.throw("The total of percentages for distributing charges should add up to 100")
			}
		}
	}
}

frappe.ui.form.on('Landed Cost Purchase Receipt', { 
	receipt_document:function(frm,cdt,cdn) {
		let row = locals[cdt][cdn]
		frappe.call({
			method:"al_ansari.al_ansari.customization.sales_order.validation_for_duplicate_PR_in_landed_cost_voucher",
			args: {
				doc:frm.doc,
			},
			callback:function (r) {
				if (r.message.length == 0)
				{			
					reset()
				}
			}
		});
		function reset() {
				// body...
				frappe.msgprint(__("Landed Cost Voucher is already created for selected Receipt Document - {0}",[row.receipt_document]))
				row.receipt_document = ""
			}
	}
})


frappe.ui.form.on('Landed Cost Item', { 
	percentage:function(frm,cdt,cdn) {
		let row = locals[cdt][cdn]
		if (frm.doc.total_taxes_and_charges && frm.doc.percentage_based ==1 && frm.doc.distribute_charges_based_on == "Distribute Manually") {
			row.applicable_charges = frm.doc.total_taxes_and_charges * flt(row.percentage / 100)
		}
	}
})