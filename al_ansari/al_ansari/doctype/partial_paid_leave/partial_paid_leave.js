// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Partial Paid Leave', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Partial Paid Leave Item', {
	fraction_of_daily_salary_per_leave: function(frm,cdt,cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(d.doctype, d.name, 'deduction', (1 - d.fraction_of_daily_salary_per_leave));
	}
});
