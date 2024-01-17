// Copyright (c) 2023, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Credit Application', {
	validate: function(frm) {
		if (frm.doc.email) {
			var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

			if (!frm.doc.email.match(validRegex)) {

				frappe.throw("Invalid Email Address!");
			}
		}
	},
	refresh: function(frm) {
		var company_currency = frappe.get_doc(":Company", frm.doc.company).default_currency;
		frm.set_currency_labels([
            "overall_business_volume",
        ], company_currency, "business_during_last_three_years");
		frm.set_currency_labels([
            "business_with_al_ansari",
        ], company_currency, "business_during_last_three_years");
	}
});
