frappe.ui.form.on('Asset Repair', { 
	refresh:function(frm) {
		frm.set_query("purchase_invoice", function() {
	        return {
	            "filters": {
	                "company": frm.doc.company,
	                "asset_cost_center": frm.doc.cost_center,
	                "asset": frm.doc.asset,
	            }
	        };
	    });
	}
})