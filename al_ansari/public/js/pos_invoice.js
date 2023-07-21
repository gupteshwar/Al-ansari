frappe.ui.form.on('POS Invoice',{ 
validate: function(frm) {
	// if return then auto update payments table with amount
	// incase multiple payment_modes the and default is there then return against default 
	// else return amount updated in the first non default mode and rest set to zero
	if(frm.doc.is_return==1) {
		var net_total = 0
		for(var i = 0; i<frm.doc.items.length;i++) {
			net_total = net_total+frm.doc.items[i].net_amount
		}

		if(net_total != frm.doc.paid_amount) {
			for(var p = 0;p<frm.doc.payments.length;p++) {
				if ((frm.doc.payments[p]["default"]==1) && (frm.doc.payments[p]["amount"] != net_total && frm.doc.payments[p]["amount"] !=0) && (frm.doc.paid_amount != net_total)){
					frm.doc.payments[p]["base_amount"] = net_total
					frm.doc.payments[p]["amount"] = net_total
					frm.set_value('paid_amount',net_total)
				} else if((frm.doc.payments[p]["default"]!=1) && (frm.doc.payments[p]["amount"] != net_total && frm.doc.payments[p]["amount"] !=0) && (frm.doc.paid_amount != net_total)){
					frm.doc.payments[p]["amount"] = net_total
					frm.doc.payments[p]["base_amount"] = net_total
					frm.set_value('paid_amount',net_total)
				} else {
					frm.doc.payments[p]["amount"] = 0
					frm.doc.payments[p]["base_amount"] = 0
				}
				frm.refresh_field("payments")
				
			}
		}	
	}
	// checkbox update to enable or disable workflow on payment_mode = Bank
	for(var q = 0;q<frm.doc.payments.length;q++) {
		if(frm.doc.payments[q]["type"] == "Bank" && frm.doc.payments[q]["base_amount"]!=0) {
				frm.set_value("payment_mode_is_bank",1)
			}else if(frm.doc.payments[q]["type"] == "Bank" && frm.doc.payments[q]["base_amount"]==0) {
				frm.set_value("payment_mode_is_bank",0)
			}
	}
}
});